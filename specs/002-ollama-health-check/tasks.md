# Tasks: Ollama Model Health Check

Feature: Ollama Model Health Check
Date: 2025-12-26
Source: specs/002-ollama-health-check/plan.md, spec.md

## Phase 1: Setup

- [X] T001 Add `httpx` to runtime dependencies in pyproject.toml (move from dev if present) at pyproject.toml
- [X] T002 [P] Add Makefile target `ollama-ps` to run `ollama ps` with echo help at Makefile
- [X] T003 [P] Add Makefile target `ollama-check` to verify model via `ollama ps` (accept `MODEL` var) at Makefile
- [X] T004 Document env vars `OLLAMA_HOST`, `OLLAMA_MODEL` in README and link to feature quickstart at README.md
- [X] T005 [P] Ensure subprocess/http timeouts set to 5s default constants in src/services/semantic_search.py

## Phase 2: Foundational

- [X] T006 Update HealthResponse schema to include `model_name` field (keep existing fields) at src/api/schemas.py
- [X] T006a Make `ollama` a required enum (remove default "unknown"; allowed: connected, model_not_running, disconnected) at src/api/schemas.py
- [X] T007 Add `health snapshot` shape definition (typed dict or dataclass) in src/api/schemas.py for reuse at src/api/schemas.py
- [X] T008 Prepare app state slot `app.state.health_snapshot` (type annotate) in src/main.py
- [X] T009 Ensure `SemanticSearchService` exposes configured `model` and base name helper at src/services/semantic_search.py

## Phase 3: User Story 1 (P1) — System Operators Monitor Model Readiness

Goal: Health endpoint reflects startup-time Ollama connectivity and model readiness; returns 200 (healthy/degraded) or 503 (unhealthy).
Independent Test Criteria: Start with three startup states; `/health` returns matching status/body and HTTP code without re-checking.

- [X] T010 [US1] Implement `compute_startup_health()` returning snapshot dict with keys: status, ollama, ollama_message, model_name, resources_loaded at src/services/semantic_search.py
- [X] T011 [US1] Compute and cache snapshot at startup (`lifespan`) into `app.state.health_snapshot` (no live checks in route) at src/main.py
- [X] T012 [US1] Update `/health` route to return cached snapshot only; map HTTP 200 (healthy/degraded) and 503 (unhealthy) at src/api/routes.py
- [X] T013 [P] [US1] Add/adjust contract tests for healthy/degraded/unhealthy: expect 200 for healthy/degraded, 503 for unhealthy; assert fields `status`, `resources_loaded`, `ollama`, `ollama_message`, `model_name`; restrict `ollama` values to [connected, model_not_running, disconnected] at tests/contract/test_health_responses.py
- [X] T014 [P] [US1] Add unit tests for `compute_startup_health()` using mocks for httpx/subprocess at tests/unit/test_semantic_search.py
- [X] T015 [P] [US1] Add integration tests to assert startup snapshot drives responses (simulate three states), expect 503 for unhealthy, and verify two consecutive `/health` calls return identical payloads at tests/integration/test_health_api.py

## Phase 4: User Story 2 (P2) — Automated Health Checks Report Specific Issues

Goal: Health response includes actionable messages, remains consistent across repeated calls (no runtime re-checks).
Independent Test Criteria: Multiple `/health` requests return identical startup-derived status/message; degraded includes remediation.

- [X] T016 [US2] Ensure `ollama_message` includes remediation for degraded (e.g., "Run 'ollama run <model>' and restart service") at src/services/semantic_search.py
- [X] T017 [US2] Verify route does not call live checks; only reads `app.state.health_snapshot` (consistency across repeated requests) at src/api/routes.py
- [X] T018 [P] [US2] Add contract test asserting actionable `ollama_message` content for degraded/unhealthy at tests/contract/test_health_responses.py
- [X] T019 [P] [US2] Add integration test for consistency over repeated requests at tests/integration/test_health_api.py

## Phase 5: User Story 3 (P3) — Health Status Includes Model Configuration

Goal: Health response includes configured `model_name` reflecting env/config at startup.
Independent Test Criteria: Changing `OLLAMA_MODEL` then restarting reflects new `model_name` in health response.

- [X] T020 [US3] Source model name from `SemanticSearchService.model` into snapshot `model_name` at src/services/semantic_search.py
- [X] T021 [P] [US3] Add test that sets `OLLAMA_MODEL` and verifies returned `model_name` after restart at tests/integration/test_health_api.py
- [X] T022 [P] [US3] Add unit test for base-name matching against `ollama ps` output variations at tests/unit/test_semantic_search.py

## Final Phase: Polish & Cross-Cutting

- [X] T023 Add examples in openapi contract for all three states at specs/002-ollama-health-check/contracts/openapi.yaml
- [X] T024 Sync quickstart with Makefile helpers and restart guidance at specs/002-ollama-health-check/quickstart.md
- [X] T025 [P] Ensure 5s timeouts: httpx requests, subprocess run; centralize constants at src/services/semantic_search.py
- [X] T026 [P] Update README with monitoring notes and status code rules at README.md
- [X] T027 [P] Add unit tests that cover timeout/failure branches for startup checks (HTTP timeout, `ollama ps` timeout/CLI missing) at tests/unit/test_semantic_search.py

## Dependencies (Story Order)

- US1 → US2 → US3
- Foundational tasks (Phase 2) must complete before US1.

Graph:
- Phase 1 → Phase 2 → US1 → US2 → US3 → Polish

## Parallel Execution Examples

- US1: T013 (contract), T014 (unit), T015 (integration) can run in parallel.
- US2: T018 (contract) and T019 (integration) in parallel once T017 is done.
- US3: T021 and T022 in parallel after T020 is implemented.
- Setup: T002 and T003 can be done in parallel.

## Implementation Strategy

- MVP: Deliver Phase 1–2 and US1 only (startup snapshot + `/health` using cached status with HTTP 200/503).
- Incremental: Add US2 (actionable messages, consistency tests), then US3 (model_name exposure). Finish with Polish.

## Validation

- All tasks follow the required checklist format with IDs, optional [P], and [US#] labels for story phases, and include explicit file paths.
