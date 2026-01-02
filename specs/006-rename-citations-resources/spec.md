# Feature Specification: Rename Citations to Resources in Agent Endpoint

**Feature Branch**: `006-rename-citations-resources`  
**Created**: January 1, 2026  
**Status**: Draft  
**Input**: User description: "in the 'experimental/agent' endpoint, we use the term 'citations' in the response as an attribute. rename that to 'resources'"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - API Consumer Updates Response Handling (Priority: P1)

API consumers (developers integrating with the agent endpoint) need to update their code to use the new "resources" attribute name instead of "citations" when parsing agent responses with sources enabled.

**Why this priority**: This is the core change - renaming the response attribute affects all users of the API. The terminology change makes the API more consistent with the rest of the system, which already uses "resources" throughout other endpoints.

**Independent Test**: Can be fully tested by calling the agent endpoint with `include_sources=true` and verifying the response contains a "resources" field instead of "citations", and that the data structure remains unchanged.

**Acceptance Scenarios**:

1. **Given** an agent request with `include_sources=true`, **When** the agent responds with sources, **Then** the response contains a "resources" field (not "citations")
2. **Given** an agent request with `include_sources=false`, **When** the agent responds, **Then** the response does not contain either "resources" or "citations" fields
3. **Given** existing code using the "citations" field, **When** updated to use "resources", **Then** all data and structure remain identical except for the field name

---

### User Story 2 - Backward Compatibility Documentation (Priority: P2)

API consumers need clear documentation about the field name change, including migration guidance and version information, to update their integrations smoothly.

**Why this priority**: While not technically required for the change to work, proper documentation prevents confusion and support requests, enabling smooth adoption by API consumers.

**Independent Test**: Documentation can be independently reviewed to verify it clearly explains the change, provides before/after examples, and includes migration steps.

**Acceptance Scenarios**:

1. **Given** the API documentation, **When** a developer reads about the agent endpoint, **Then** they see the field is named "resources" with no mention of "citations"
2. **Given** release notes or migration guide, **When** a developer reads them, **Then** they understand the field was renamed and see code examples showing the update

---

### Edge Cases

- What happens when no sources are found? (Should return empty "resources" array or omit the field entirely based on `include_sources` flag)
- How do automated tests validate the field name change? (All tests referencing "citations" must be updated to expect "resources")
- Are there any cached responses or documentation examples that still use "citations"? (Must be updated consistently)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST return agent responses with a "resources" field when `include_sources=true`, not "citations"
- **FR-002**: System MUST maintain identical data structure and content within the renamed field (only the field name changes)
- **FR-003**: Response schema MUST define the field as "resources" in all API documentation and OpenAPI specifications
- **FR-004**: System MUST omit both "resources" and "citations" fields when `include_sources=false`
- **FR-005**: All code comments, docstrings, and internal documentation MUST use "resources" terminology instead of "citations"
- **FR-006**: All automated tests MUST validate responses use "resources" field name
- **FR-007**: Class names and type definitions related to agent citations MUST be updated to use "resources" terminology for consistency

### Key Entities

- **AgentResponse**: The response object returned by the experimental/agent endpoint, containing answer, query, meta, and optionally resources
- **Resource**: Individual resource items (currently called Citation) containing title, url, and summary fields - represents source material referenced in the agent's answer

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All agent endpoint responses with sources enabled return a "resources" field with zero occurrences of "citations" field
- **SC-002**: All existing tests pass after field rename with no changes to test expectations other than field name
- **SC-003**: API documentation and OpenAPI schema accurately reflect the "resources" field name with no references to "citations"
- **SC-004**: Code search across entire codebase shows zero occurrences of "citations" in agent endpoint context (excluding git history and archived documentation)
