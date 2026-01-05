# Tasks: Boolean Resource Validation with Hallucination Filtering

**Input**: Design documents from `/specs/007-bool-resource-validation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included per constitution requirement - all new features MUST have corresponding tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification of existing infrastructure

- [X] T001 Verify Python 3.13 environment and uv package manager installed
- [X] T002 [P] Verify existing test structure (unit/integration/contract directories)
- [X] T003 [P] Verify quality gates are executable (pytest, ruff, mypy)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add NO_VALID_RESOURCES error code to AgentErrorCode enum in src/api/schemas.py
- [X] T005 [P] Verify ErrorResponse schema supports 404 error cases in src/api/schemas.py
- [X] T006 [P] Verify LinkVerifier.verify_link exists and returns bool in src/utils/link_verifier.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Receive Only Valid Resources (Priority: P1) 🎯 MVP

**Goal**: Enable API consumers to receive only validated, non-hallucinated resources from the experimental endpoint, ensuring data quality and reliability for downstream consumers.

**Independent Test**: Make API requests to the experimental endpoint with include_sources=true and verify that the response contains only resources that pass validation criteria, with no hallucinated entries included.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [US1] Create contract test for HTTP 404 response schema in tests/contract/test_agent_contract.py::test_agent_404_no_valid_resources
- [X] T008 [P] [US1] Create integration test for mixed valid/invalid resources in tests/integration/test_agent_api.py::test_agent_filters_invalid_resources
- [X] T009 [P] [US1] Create integration test for all resources invalid (404) in tests/integration/test_agent_api.py::test_agent_all_invalid_returns_404
- [X] T010 [P] [US1] Create integration test for all resources valid in tests/integration/test_agent_api.py::test_agent_all_valid_included
- [X] T011 [P] [US1] Create unit test for boolean validation return in tests/unit/test_agent_orchestrator.py::test_validate_resource_tool_returns_bool

### Implementation for User Story 1

- [X] T012 [US1] Modify _validate_resource_tool to return bool instead of string in src/services/agent/react_agent.py:136-162
- [X] T013 [US1] Update _validate_resource_tool docstring with new return type and exception behavior in src/services/agent/react_agent.py:136-162
- [X] T014 [US1] Add import for logging module at top of src/api/routes.py
- [X] T015 [US1] Implement resource filtering logic in run_experimental_agent function in src/api/routes.py:255-288
- [X] T016 [US1] Add validated_resources list and validation loop in src/api/routes.py (after line 277)
- [X] T017 [US1] Add HTTP 404 response for all-resources-invalid case in src/api/routes.py (check validated_resources list)
- [X] T018 [US1] Ensure resource order preservation per FR-007 in filtering loop in src/api/routes.py
- [X] T019 [US1] Run all User Story 1 tests and verify they pass: uv run pytest tests/unit/test_agent_orchestrator.py::test_validate_resource_tool_returns_bool tests/integration/test_agent_api.py::test_agent_filters_invalid_resources tests/integration/test_agent_api.py::test_agent_all_invalid_returns_404 tests/integration/test_agent_api.py::test_agent_all_valid_included tests/contract/test_agent_contract.py::test_agent_404_no_valid_resources

**Checkpoint**: At this point, User Story 1 should be fully functional - API consumers receive only valid resources, with HTTP 404 when all fail validation

---

## Phase 4: User Story 2 - Hallucination Detection Logging (Priority: P2)

**Goal**: Enable system administrators and developers to monitor data quality by logging all hallucination detection events with sufficient detail for debugging and analysis.

**Independent Test**: Trigger validation failures and verify that hallucination events are properly logged at WARNING level with resource details, and that multiple failures generate separate log entries.

### Tests for User Story 2

- [X] T020 [P] [US2] Create integration test for WARNING level logging in tests/integration/test_agent_api.py::test_agent_logs_hallucinations_at_warning_level
- [X] T021 [P] [US2] Create integration test for multiple hallucinations logged separately in tests/integration/test_agent_api.py::test_agent_logs_multiple_hallucinations
- [X] T022 [P] [US2] Create integration test for validation exception logging at ERROR level in tests/integration/test_agent_api.py::test_agent_logs_validation_exceptions
- [X] T023 [P] [US2] Create unit test for logging failure suppression in tests/unit/test_agent_orchestrator.py::test_logging_failure_suppressed

### Implementation for User Story 2

- [X] T024 [US2] Add WARNING level logging for is_valid==False in src/api/routes.py filtering loop (within try block)
- [X] T025 [US2] Add structured logging with extra={url, title, query} for hallucinations in src/api/routes.py
- [X] T026 [US2] Wrap hallucination logging in try/except to suppress failures (FR-009) in src/api/routes.py
- [X] T027 [US2] Add ERROR level logging for validation exceptions with exc_info=True in src/api/routes.py (except block)
- [X] T028 [US2] Add structured logging with extra={url, query} for exceptions in src/api/routes.py
- [X] T029 [US2] Wrap exception logging in try/except to suppress failures (FR-009) in src/api/routes.py
- [X] T030 [US2] Verify no hallucination logs when all resources valid in tests/integration/test_agent_api.py::test_no_logs_when_all_valid
- [X] T031 [US2] Run all User Story 2 tests and verify they pass: uv run pytest tests/integration/test_agent_api.py::test_agent_logs_hallucinations_at_warning_level tests/integration/test_agent_api.py::test_agent_logs_multiple_hallucinations tests/integration/test_agent_api.py::test_agent_logs_validation_exceptions tests/unit/test_agent_orchestrator.py::test_logging_failure_suppressed tests/integration/test_agent_api.py::test_no_logs_when_all_valid

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - filtering works correctly AND all hallucinations are properly logged

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Verification, testing, and quality assurance across all stories

- [X] T032 [P] Run full test suite to ensure no regressions: uv run pytest
- [X] T033 [P] Run ruff linting and fix any errors: uv run ruff check .
- [X] T034 [P] Run mypy type checking and fix any errors: uv run mypy src/
- [X] T035 [P] Run ruff formatting check: uv run ruff format --check .
- [X] T036 Verify all existing tests still pass (no regression): uv run pytest tests/
- [X] T037 [P] Verify experimental endpoint-only changes (no other endpoints modified)
- [X] T038 [P] Manual testing per quickstart.md scenarios (optional, for validation)
- [X] T039 Review and update CLAUDE.md if needed with any new patterns discovered
- [X] T040 Final validation: Run complete quality gate sequence (pytest && ruff check . && mypy src/ && ruff format --check .)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational (Phase 2) - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational (Phase 2) - No dependencies on US1, but logically builds on filtering
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Independently testable via HTTP 404 and filtering behavior
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independently testable via log capture, but logically enhances US1 with observability

### Within Each User Story

- Tests MUST be written FIRST and FAIL before implementation (TDD approach per constitution)
- T012-T013 (validation function) can be done first or in parallel with route changes
- T014-T018 (filtering logic) must be done sequentially as they build on each other
- All tests for a story can run in parallel once implementation is complete

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003 can run in parallel

**Phase 2 (Foundational)**:
- T005, T006 can run in parallel (different files/verification tasks)

**Phase 3 (User Story 1) - Tests**:
- T007, T008, T009, T010, T011 can all be written in parallel (different test files/functions)

**Phase 3 (User Story 1) - Implementation**:
- T012-T013 (react_agent.py) can run in parallel with T014 (routes.py import)
- T015-T018 must be sequential (same file, interdependent)

**Phase 4 (User Story 2) - Tests**:
- T020, T021, T022, T023 can all be written in parallel (different test files/functions)

**Phase 4 (User Story 2) - Implementation**:
- T024-T029 must be sequential (same file, building logging into existing filtering logic)

**Phase 5 (Polish)**:
- T032, T033, T034, T035 can run in parallel (independent quality checks)
- T037, T038, T039 can run in parallel

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together (write in parallel):
Task: "Create contract test for HTTP 404 response schema in tests/contract/test_agent_contract.py::test_agent_404_no_valid_resources"
Task: "Create integration test for mixed valid/invalid resources in tests/integration/test_agent_api.py::test_agent_filters_invalid_resources"
Task: "Create integration test for all resources invalid (404) in tests/integration/test_agent_api.py::test_agent_all_invalid_returns_404"
Task: "Create integration test for all resources valid in tests/integration/test_agent_api.py::test_agent_all_valid_included"
Task: "Create unit test for boolean validation return in tests/unit/test_agent_orchestrator.py::test_validate_resource_tool_returns_bool"
```

---

## Parallel Example: User Story 2 Tests

```bash
# Launch all tests for User Story 2 together (write in parallel):
Task: "Create integration test for WARNING level logging in tests/integration/test_agent_api.py::test_agent_logs_hallucinations_at_warning_level"
Task: "Create integration test for multiple hallucinations logged separately in tests/integration/test_agent_api.py::test_agent_logs_multiple_hallucinations"
Task: "Create integration test for validation exception logging at ERROR level in tests/integration/test_agent_api.py::test_agent_logs_validation_exceptions"
Task: "Create unit test for logging failure suppression in tests/unit/test_agent_orchestrator.py::test_logging_failure_suppressed"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T006) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T007-T019)
4. **STOP and VALIDATE**: Run User Story 1 tests independently (T019)
5. Verify HTTP 404 response and resource filtering work correctly
6. Deploy/demo if ready (MVP complete!)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T006)
2. Add User Story 1 → Test independently (T019) → Deploy/Demo (MVP!)
   - **Value**: API consumers now receive only valid resources
3. Add User Story 2 → Test independently (T031) → Deploy/Demo
   - **Value**: Admins can now monitor hallucination patterns
4. Each story adds observability without breaking previous functionality

### Parallel Team Strategy

With 2 developers:

1. Both complete Setup + Foundational together (T001-T006)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T007-T019) - Core filtering
   - **Developer B**: User Story 2 tests (T020-T023) - Can start writing tests in parallel
3. Once US1 implementation done, Developer B adds logging (T024-T031)
4. Both run quality gates together (T032-T040)

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 3 tasks
- **Phase 3 (US1)**: 13 tasks (5 tests + 8 implementation)
- **Phase 4 (US2)**: 12 tasks (5 tests + 7 implementation)
- **Phase 5 (Polish)**: 9 tasks
- **Total**: 40 tasks

---

## Notes

- [P] tasks = different files or independent verification, can run in parallel
- [US1]/[US2] labels map tasks to specific user stories for traceability
- Each user story is independently completable and testable per constitution requirement
- Tests must be written FIRST and fail before implementation (TDD)
- Commit after each logical task group or checkpoint
- Stop at any checkpoint to validate story independently
- User constraint honored: Only experimental endpoint modified (T037 verifies this)
- All quality gates must pass before merge (T040)
