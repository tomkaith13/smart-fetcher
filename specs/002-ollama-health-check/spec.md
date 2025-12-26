# Feature Specification: Ollama Model Health Check

**Feature Branch**: `002-ollama-health-check`  
**Created**: December 26, 2025  
**Status**: Draft  
**Input**: User description: "Add a new feature that checks if the ollama model is running and have that reflect in the health endpoint. for ex, if gpt-oss is running and can serve inference or not"

## Clarifications

### Session 2025-12-26

- Q: What HTTP status code should the health endpoint return for each health state (healthy, degraded, unhealthy)? → A: Return HTTP 200 for healthy, 200 for degraded, 503 for unhealthy
- Q: How should the existing health response structure (with status and resources_loaded) be modified to include Ollama status? → A: Add new Ollama fields (ollama, ollama_message, model_name) alongside existing status and resources_loaded fields
- Q: Should health checks cache results or perform live checks on every request to reduce load from calling ollama ps frequently? → A: Check ollama ps only once at service startup, not on every health check request

## User Scenarios & Testing *(mandatory)*

### User Story 1 - System Operators Monitor Model Readiness (Priority: P1)

System operators and monitoring tools need to verify whether the inference model (Ollama) was running and ready at service startup. This provides visibility into the service'\''s initialization state and helps diagnose startup failures related to model availability.

**Why this priority**: This is the core value of the feature. Without startup model status visibility, operators cannot distinguish between model configuration issues and other service problems during deployment and initialization.

**Independent Test**: Can be fully tested by starting the service with different Ollama states and verifying the health endpoint reflects the startup-time model status. Delivers immediate value by providing visibility into service initialization.

**Acceptance Scenarios**:

1. **Given** Ollama service is running and the configured model (e.g., gpt-oss) was loaded at service startup, **When** a user or monitoring system calls the health endpoint, **Then** the response indicates "healthy" status with confirmation that the model was verified at startup, and HTTP status code is 200
2. **Given** Ollama service was running at startup but the configured model was not loaded, **When** the health endpoint is called, **Then** the response indicates "degraded" status with a message explaining which model was not running at startup, and HTTP status code is 200
3. **Given** Ollama service was unreachable at service startup, **When** the health endpoint is called, **Then** the response indicates "unhealthy" status with a message that the Ollama service could not be contacted at startup, and HTTP status code is 503

---

### User Story 2 - Automated Health Checks Report Specific Issues (Priority: P2)

Automated monitoring systems (e.g., Kubernetes liveness/readiness probes, external monitoring tools) need to receive structured health information that was determined at service startup.

**Why this priority**: Enhances operational efficiency by providing actionable startup validation information in health responses. Operators can immediately understand startup state without re-checking Ollama.

**Independent Test**: Can be tested by starting the service in different failure scenarios (model not loaded, Ollama down) and verifying the health endpoint consistently returns the appropriate startup status.

**Acceptance Scenarios**:

1. **Given** the health endpoint returns a degraded status, **When** an operator reads the response message, **Then** the message includes the specific model name that was not running at startup and a suggested remediation action (restart service after starting model)
2. **Given** the service has started successfully, **When** multiple health checks are performed, **Then** they consistently return the same startup-time status without re-checking Ollama state

---

### User Story 3 - Health Status Includes Model Configuration (Priority: P3)

Operators troubleshooting issues need to verify which model the service is configured to use and its startup verification status.

**Why this priority**: Helps with configuration validation and troubleshooting when multiple models or environments are in use. Prevents confusion when the wrong model name is configured.

**Independent Test**: Can be tested by calling the health endpoint and verifying the response includes the configured model name and startup status. Validates configuration without requiring search operations.

**Acceptance Scenarios**:

1. **Given** the system is configured with a specific model name (e.g., "gpt-oss:20b"), **When** the health endpoint is called, **Then** the response includes the configured model name and its startup verification status
2. **Given** the model configuration changes (e.g., environment variable update), **When** the service restarts and health is checked, **Then** the new model name and its startup verification status are reflected in health responses

---

### Edge Cases

- What happens when the Ollama service is running but responding very slowly during startup (timeouts)?
  - System should treat slow responses (>5 seconds) at startup as unhealthy and capture that status
- What happens when the \`ollama ps\` command is not available or returns unexpected output format at startup?
  - System should gracefully handle command failures and set degraded/unhealthy status that persists for the service lifetime
- What happens when multiple models are running but not the configured one at startup?
  - System should correctly identify that the specific configured model was not running and set degraded status
- What happens during the window when a model is starting up during service initialization?
  - System should wait briefly (within the 5-second timeout) or report degraded status if model is not yet ready
- What happens if the model stops or crashes after the service has started?
  - Health endpoint will continue reporting the startup-time status; operators must restart the service to re-verify model state

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST check Ollama service connectivity once at service startup as part of initialization
- **FR-002**: System MUST verify that the specific configured model is loaded and running in Ollama during service startup
- **FR-003**: System MUST distinguish between three health states: healthy (Ollama connected and model running at startup), degraded (Ollama connected but model not running at startup), and unhealthy (Ollama not reachable at startup)
- **FR-004**: Health endpoint MUST return the startup-time status of Ollama connectivity with descriptive messages
- **FR-005**: Health endpoint MUST return the startup-time status of the configured model (was running or not running at startup)
- **FR-006**: Health endpoint MUST include the name of the configured model that was checked at startup
- **FR-007**: System MUST handle Ollama service timeouts gracefully during startup and capture them as unhealthy status
- **FR-008**: System MUST handle cases where the model checking mechanism fails during startup and set appropriate status
- **FR-009**: Startup health checks MUST complete within a reasonable timeout period (5 seconds maximum)
- **FR-010**: Health endpoint MUST provide actionable information to operators (e.g., which model to start before restarting service)
- **FR-011**: Health endpoint MUST return HTTP 200 status code for healthy and degraded states
- **FR-012**: Health endpoint MUST return HTTP 503 status code for unhealthy state (Ollama unreachable at startup)
- **FR-013**: Health endpoint MUST maintain backward compatibility by preserving existing response fields (status, resources_loaded)
- **FR-014**: Health endpoint MUST add new Ollama-specific fields (ollama status, ollama_message, model_name) to the response without removing or renaming existing fields
- **FR-015**: System MUST NOT re-check Ollama or model status on subsequent health endpoint requests after startup
- **FR-016**: Health status determined at startup MUST persist for the entire service lifetime until restart

### Key Entities *(include if feature involves data)*

- **Health Status**: Represents the overall system health state determined at startup with three possible values (healthy, degraded, unhealthy), includes Ollama connectivity status, model running status, configured model name, and descriptive messages for operators
- **Model Configuration**: Represents the Ollama model that the system expects to use for inference, includes model name and optional version/tag (e.g., "gpt-oss:20b")
- **Health Response**: Contains overall status field, resources_loaded count (existing), plus new Ollama-specific fields (ollama status, ollama_message, model_name) maintaining backward compatibility

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Service startup completes within 5 seconds including Ollama model verification
- **SC-002**: Health endpoint returns responses in under 100 milliseconds since no runtime checks are performed
- **SC-003**: 100% of service starts correctly identify when Ollama service was unreachable at startup
- **SC-004**: 100% of service starts correctly identify when the configured model was not running at startup
- **SC-005**: Health response messages include actionable information (model name and remediation steps) for all degraded and unhealthy states
- **SC-006**: Operators can determine the exact startup health issue (Ollama down vs. model not loaded at startup) from the health endpoint response without additional investigation in 95% of cases
- **SC-007**: Health endpoint requests have zero impact on Ollama service since no runtime checks are performed

## Assumptions

1. **Ollama Service Detection**: The system assumes Ollama exposes a standard HTTP API endpoint (typically \`/api/tags\`) that can be used to verify service connectivity at startup. This is consistent with current Ollama architecture.

2. **Model Listing Command**: The system assumes the \`ollama ps\` command-line tool is available in the environment where the service runs and can be executed at startup to list running models. This is the standard method for checking model status.

3. **Model Name Format**: The system assumes model names follow Ollama'\''s standard format (e.g., "gpt-oss:20b" or "gpt-oss") and that the base model name (part before colon) is sufficient for matching in the \`ollama ps\` output.

4. **Startup-Only Verification**: The system assumes model status verification at startup is sufficient, and that runtime model state changes (crashes, stops) are rare enough that service restart is an acceptable remediation. Real-time model monitoring is not required.

5. **Single Model Configuration**: The system assumes a single primary model is configured for the semantic search service. Scenarios with multiple models or model failover are out of scope for this feature.

6. **Timeout Values**: The system assumes 5-second timeouts are appropriate for both Ollama connectivity checks and model verification commands during startup. This balances responsiveness with reliability in typical network conditions.

7. **Error Handling**: The system assumes that any failure in connectivity or model checking during startup should be captured and reported as degraded/unhealthy status that persists throughout service lifetime. The health endpoint itself should never fail (except returning 503 for unhealthy state).

8. **Service Restart Acceptable**: The system assumes that if the model state changes after service startup (model stops, crashes, or starts), restarting the service is an acceptable operational procedure to re-verify and update health status.

## Dependencies

- **Ollama Service**: The feature depends on Ollama service being installed and the \`ollama\` command-line tool being available in the system PATH at startup time.

- **HTTP Client**: The feature requires an HTTP client library capable of making requests to the Ollama API endpoint with timeout support during startup.

- **Existing Health Endpoint**: This feature enhances the existing health endpoint structure and must maintain backward compatibility with current health response format.

## Out of Scope

- **Model Performance Metrics**: This feature checks if the model was running at startup but does not measure inference performance, response time, or quality metrics.

- **Automatic Model Starting**: The feature reports when a model was not running at startup but does not automatically start or load models.

- **Model Version Verification**: While the feature checks if a model was running at startup, it does not verify that the loaded model version matches an expected version.

- **Multiple Model Support**: Checking the status of multiple models simultaneously is not included in this feature.

- **Historical Health Tracking**: The feature provides startup-time health status but does not store or report historical health data or uptime metrics.

- **Runtime Model Monitoring**: The feature verifies model status only at startup and does not monitor for runtime model state changes (crashes, stops, starts). Operators must restart the service to refresh health status.

- **Detailed Resource Metrics**: The feature does not report on Ollama resource usage (CPU, memory, GPU) or model-specific resource consumption.
