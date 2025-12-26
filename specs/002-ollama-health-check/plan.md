# Implementation Plan: Ollama Model Health Check

**Branch**: `002-ollama-health-check` | **Date**: 2025-12-26 | **Spec**: specs/002-ollama-health-check/spec.md
**Input**: Feature specification from `specs/002-ollama-health-check/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

- Primary requirement: Expose Ollama model readiness in the `/health` endpoint with three states: healthy (connected + model verified), degraded (connected, model not verified), unhealthy (Ollama unreachable at startup). Preserve existing fields and add Ollama-specific fields.
- Technical approach: Perform a single verification at service startup (HTTP reachability + `ollama ps` for model presence). Cache this result in `app.state` and return it in `/health` without re-checking at runtime. Maintain backward-compatible response structure and status codes (200 for healthy/degraded, 503 for unhealthy).

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.13  
**Primary Dependencies**: FastAPI, Pydantic v2, httpx (already used), subprocess (stdlib), pytest  
**Storage**: N/A  
**Testing**: pytest with unit, integration, and contract tests (existing structure)  
**Target Platform**: macOS/Linux server  
**Project Type**: Single backend service  
**Performance Goals**: Health endpoint <100ms p50 (no runtime checks)  
**Constraints**: No new runtime dependencies unless approved; startup checks must complete ≤5s  
**Scale/Scope**: Local service with frequent health polling by monitors

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates determined per Smart Fetcher Constitution v2.0.0

- I. Code Quality: All new/changed Python must be fully type-annotated, small functions, ruff clean, with docstrings.
- II. Testing Standards: Add unit tests for startup health cache logic, contract tests for `/health` schema, and integration tests simulating startup states. Mock external services in unit tests.
- III. UX Consistency: Maintain consistent JSON response structure; 200 for healthy/degraded, 503 for unhealthy. Provide actionable `ollama_message`.

Gate Status (Pre-Design): PASS — approach aligns; tests planned in Phase 2. No violations anticipated.

Re-check (Post-Design): PASS — response structure consistent, test plan covers unit/contract/integration, actionable messages defined. No exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Use existing single-project layout. Touch points:
- src/services/semantic_search.py (add startup-check API + cached status)
- src/api/schemas.py (ensure HealthResponse supports fields)
- src/api/routes.py (return startup-cached status, set HTTP code)
- src/main.py (or app factory) to perform startup verification and store in `app.state`
- Makefile (add helper targets to verify Ollama model)
- tests/{unit,integration,contract} (add/update tests)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Phase 0: Research (Resolved Unknowns)

- Decision: Startup-only verification (no runtime checks)
  - Rationale: Minimizes runtime overhead and external coupling; aligns with user directive
  - Alternatives: Runtime checks on each request; periodic background checks
- Decision: HTTP status codes (200 healthy/degraded; 503 unhealthy)
  - Rationale: Monitoring-friendly while preserving detailed body; clear signal on unhealthy
  - Alternatives: Always 200; 503 on degraded as well
- Decision: Backward-compatible response augmentation
  - Rationale: Avoid breaking clients; additive fields `ollama`, `ollama_message`, `model_name`
  - Alternatives: Replace/rename existing fields

Output: See research.md

## Phase 1: Design & Contracts

### Data Model (docs only)

- HealthStatus (enum): healthy | degraded | unhealthy
- OllamaStatus (enum): connected | model_not_running | disconnected
- HealthResponse fields: status, resources_loaded, ollama, ollama_message, model_name

### API Contract (OpenAPI excerpt)

- GET /health → 200 (healthy/degraded) or 503 (unhealthy)
- Response schema includes fields above; examples for each state

### Makefile Helpers (planned)

- `make ollama-ps` — show running Ollama models
- `make ollama-check MODEL=?` — exit 0 if model present in `ollama ps`, else non-zero

## Phase 2: Implementation Plan (high-level steps)

1. App startup: compute startup health via `SemanticSearch` helper methods; store in `app.state.health_snapshot`
2. `HealthResponse` model: verify fields (`ollama`, `ollama_message`, `model_name`) exist; add if missing
3. `/health` route: return cached snapshot; map to HTTP 200/503
4. Makefile: add `ollama-ps` and `ollama-check` targets
5. Tests:
   - Unit: validate startup snapshot logic (mock httpx and subprocess)
   - Contract: response schema and status codes for the three states
   - Integration: simulate startup states via monkeypatch and assert responses

Dependencies: httpx is currently in dev extras but used at runtime. Decision needed: move `httpx` to main dependencies or replace with stdlib `urllib`. Pending user approval.
