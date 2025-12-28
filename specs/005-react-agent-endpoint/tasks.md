# Tasks: Experimental ReACT Agent Endpoint

Feature: 005-react-agent-endpoint
Spec: specs/005-react-agent-endpoint/spec.md
Plan: specs/005-react-agent-endpoint/plan.md
Contracts: specs/005-react-agent-endpoint/contracts/openapi.yaml

## Phase 1: Setup

- [ ] T001 Verify DSPy installed and accessible in environment
- [ ] T002 Document env vars in README: MODEL_NAME=gpt-oss:20b, TIMEOUT_SEC=5
- [ ] T003 [P] Add config defaults for agent in src/api/schemas.py (constants section)
- [ ] T004 Ensure ruff/mypy/pytest configs align with constitution in pyproject.toml
- [ ] T005 [P] Create src/services/agent/ directory for orchestrator modules

## Phase 2: Foundational

- [ ] T006 Add error codes enum in src/api/schemas.py (TOOL_TIMEOUT, INTERNAL_ERROR)
- [ ] T007 [P] Add structured JSON-lines logger in src/utils/agent_logger.py
- [ ] T008 Wire Ollama DSPy model selection: gpt-oss:20b via env in src/services/agent/react_agent.py

## Phase 3: User Story 1 (P1) — Final Answer without Citations

Goal: Single-turn query returns final answer; agent may use NL search and validation tools internally.
Independent Test Criteria: POST /experimental/agent returns an answer within 5s; no citations unless requested.

- [ ] T009 [US1] Implement DSPy `Tool` wrapper: nl_search(query) using src/services/nl_search_service.py
- [ ] T010 [P] [US1] Implement DSPy `Tool` wrapper: validate_resource(url) using src/utils/link_verifier.py
- [ ] T011 [US1] Implement ReACT orchestrator in src/services/agent/react_agent.py (final answer only)
- [ ] T012 [US1] Add route handler in src/api/routes.py: POST /experimental/agent
- [ ] T013 [US1] Update request/response models in src/api/schemas.py to match OpenAPI
- [ ] T014 [P] [US1] Log tool actions via src/utils/agent_logger.py
- [ ] T015 [US1] Unit tests: agent orchestrator behavior in tests/unit/test_agent_orchestrator.py
- [ ] T016 [US1] Contract tests: response schema compliance in tests/contract/test_agent_contract.py
- [ ] T017 [US1] Integration tests: endpoint happy path in tests/integration/test_agent_api.py

## Phase 4: User Story 2 (P2) — Answer with Validated Citations

Goal: When requested, include citations that pass validation.
Independent Test Criteria: With include_sources=true, response includes validated citations; otherwise no citations.

- [ ] T018 [US2] Propagate include_sources flag through schemas and orchestrator (src/api/schemas.py, src/services/agent/react_agent.py)
- [ ] T019 [P] [US2] Build citations list from validated resources in src/services/agent/react_agent.py
- [ ] T020 [US2] Ensure citations shape matches OpenAPI (src/api/schemas.py)
- [ ] T021 [US2] Unit tests: citations building and validation in tests/unit/test_agent_orchestrator.py
- [ ] T022 [P] [US2] Contract tests: citations response schema in tests/contract/test_agent_contract.py
- [ ] T023 [US2] Integration tests: endpoint with include_sources=true in tests/integration/test_agent_api.py

## Phase 5: User Story 3 (P3) — Graceful Uncertainty Handling

Goal: Helpful limitation message when insufficient evidence or tool failures.
Independent Test Criteria: No reliable sources → clear limitation message; timeouts → helpful message without errors.

- [ ] T024 [US3] Implement insufficient-evidence path with limitation messaging in src/services/agent/react_agent.py
- [ ] T025 [P] [US3] Handle tool timeouts and map to 504 TOOL_TIMEOUT in src/api/routes.py
- [ ] T026 [US3] Exclude invalid citations, inform user per spec in src/services/agent/react_agent.py
- [ ] T027 [US3] Unit tests: uncertainty and timeout paths in tests/unit/test_agent_orchestrator.py
- [ ] T028 [US3] Contract tests: error responses (504/400) in tests/contract/test_agent_contract.py
- [ ] T029 [US3] Integration tests: no evidence + timeout scenarios in tests/integration/test_agent_api.py

## Final Phase: Polish & Cross-Cutting

- [ ] T030 [P] Add README section and quickstart examples referencing gpt-oss:20b
- [ ] T031 Ensure consistent JSON response wrapping and machine codes across routes (src/api/routes.py)
- [ ] T032 [P] Add ruff format + check to Makefile target and run
- [ ] T033 Verify mypy strict typing across new modules
- [ ] T034 [P] Add basic runtime metrics (timing, counts) to logs in src/utils/agent_logger.py

## Dependencies

- Story order: US1 → US2 → US3
- Foundational must precede all stories: T006–T008
- Setup precedes Foundational and stories: T001–T005

## Parallel Execution Examples

- [US1]: T010 (validate_resource tool) and T014 (logging) can run in parallel once T009 is started.
- [US2]: T019 (build citations) and T022 (contract tests) can run in parallel after T018.
- [US3]: T025 (timeouts mapping) and T028 (contract error tests) can run in parallel after T024.
- Polish: T032 (ruff tasks) and T034 (metrics) can run in parallel.

## Implementation Strategy

- MVP: Complete US1 with foundational tasks (T006–T017), delivering the experimental endpoint producing final answers without citations.
- Incremental: Add US2 for citations; then US3 for uncertainty handling and robust errors.
- Testing First: Write contract tests before endpoint implementation to lock response shapes.

