---
description: "Task list for renaming citations to resources in agent endpoint"
---

# Tasks: Rename Citations to Resources in Agent Endpoint

**Input**: Design documents from `/specs/006-rename-citations-resources/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT new features - they already exist and will be updated to validate new field names.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Preparation)

**Purpose**: Verify all tests pass before refactoring begins

- [X] T001 Run full test suite to establish baseline (make test-all)

---

## Phase 2: User Story 1 - API Consumer Updates Response Handling (Priority: P1) 🎯 MVP

**Goal**: Rename "citations" field to "resources" in agent endpoint response, ensuring API consistency

**Independent Test**: Call agent endpoint with `include_sources=true` and verify response contains "resources" field instead of "citations"

### Schema and Model Updates

- [X] T002 [P] [US1] Rename Citation class to ResourceCitation in src/api/schemas.py
- [X] T003 [P] [US1] Rename AgentAnswerWithCitations to AgentAnswerWithResources in src/api/schemas.py
- [X] T004 [P] [US1] Rename citations field to resources in AgentAnswerWithResources schema in src/api/schemas.py
- [X] T005 [P] [US1] Update all docstrings and field descriptions in src/api/schemas.py to use "resources" terminology

### Service Layer Updates

- [X] T006 [US1] Update import statement from Citation to ResourceCitation in src/services/agent/react_agent.py
- [X] T007 [US1] Rename citations variable to resources in run() method in src/services/agent/react_agent.py
- [X] T008 [US1] Update response dictionary key from "citations" to "resources" in src/services/agent/react_agent.py
- [X] T009 [US1] Update all comments and docstrings in src/services/agent/react_agent.py to use "resources" terminology

### API Route Updates

- [X] T010 [US1] Update route documentation string in src/api/routes.py to use "resources" instead of "citations"

### Contract Test Updates

- [X] T011 [P] [US1] Rename test_agent_answer_with_citations_valid to test_agent_answer_with_resources_valid in tests/contract/test_agent_contract.py
- [X] T012 [P] [US1] Rename test_agent_answer_with_citations_empty to test_agent_answer_with_resources_empty in tests/contract/test_agent_contract.py
- [X] T013 [P] [US1] Rename test_agent_answer_with_citations_serialization to test_agent_answer_with_resources_serialization in tests/contract/test_agent_contract.py
- [X] T014 [P] [US1] Update test assertions to check "resources" field instead of "citations" in tests/contract/test_agent_contract.py
- [X] T015 [P] [US1] Update test_contract_compliance_success_no_citations to test_contract_compliance_success_no_resources in tests/contract/test_agent_contract.py
- [X] T016 [P] [US1] Update test_contract_compliance_success_with_citations to test_contract_compliance_success_with_resources in tests/contract/test_agent_contract.py

### Integration Test Updates

- [X] T017 [P] [US1] Update test_agent_endpoint_success to check for "resources" field in tests/integration/test_agent_api.py
- [X] T018 [P] [US1] Rename test_agent_endpoint_no_citations to test_agent_endpoint_no_resources in tests/integration/test_agent_api.py
- [X] T019 [P] [US1] Rename test_agent_endpoint_with_citations to test_agent_endpoint_with_resources in tests/integration/test_agent_api.py
- [X] T020 [P] [US1] Update field access from data["citations"] to data["resources"] in tests/integration/test_agent_api.py
- [X] T021 [P] [US1] Update all test comments to use "resources" terminology in tests/integration/test_agent_api.py

### Unit Test Updates

- [X] T022 [P] [US1] Update test_agent_run_basic comment from "citations" to "resources" in tests/unit/test_agent_orchestrator.py
- [X] T023 [P] [US1] Rename test_agent_run_with_citations to test_agent_run_with_resources in tests/unit/test_agent_orchestrator.py
- [X] T024 [P] [US1] Rename test_agent_run_citations_only_valid to test_agent_run_resources_only_valid in tests/unit/test_agent_orchestrator.py
- [X] T025 [P] [US1] Update field assertions from result["citations"] to result["resources"] in tests/unit/test_agent_orchestrator.py
- [X] T026 [P] [US1] Update all test comments to use "resources" terminology in tests/unit/test_agent_orchestrator.py

### Validation

- [X] T027 [US1] Run full test suite to verify all tests pass (make test-all)
- [X] T028 [US1] Run ruff check to verify no linting errors (ruff check .)
- [X] T029 [US1] Run mypy to verify type safety (mypy src/)
- [ ] T030 [US1] Manual API test with include_sources=true to verify "resources" field in response

**Checkpoint**: Agent endpoint now uses "resources" terminology consistently. All tests pass.

---

## Phase 3: User Story 2 - Backward Compatibility Documentation (Priority: P2)

**Goal**: Update all documentation to reflect field name change and provide migration guidance

**Independent Test**: Documentation review confirms "resources" terminology with no "citations" references, includes migration examples

### Documentation Updates

- [ ] T031 [P] [US2] Update README.md agent endpoint example to show "resources" field instead of "citations"
- [ ] T032 [P] [US2] Update README.md text references from "citations" to "resources"
- [X] T033 [P] [US2] Update specs/005-react-agent-endpoint/contracts/openapi.yaml to use "resources" field name

### Validation

- [X] T034 [US2] Grep search codebase to verify zero occurrences of "citations" in agent context (excluding git history)
- [X] T035 [US2] Review quickstart.md migration guide for completeness

**Checkpoint**: All documentation updated and consistent. No "citations" references remain.

---

## Phase 4: Polish & Final Validation

**Purpose**: Final quality checks and validation

- [X] T036 Run full test suite one final time (make test-all)
- [X] T037 Verify coverage report shows all agent code tested (pytest --cov=src/services/agent --cov=src/api)
- [X] T038 Test quickstart.md scenarios to validate migration guide accuracy
- [X] T039 Commit all changes with descriptive message

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - establish baseline
- **User Story 1 (Phase 2)**: Depends on Setup - Core refactoring
- **User Story 2 (Phase 3)**: Depends on User Story 1 - Documentation reflects code changes
- **Polish (Phase 4)**: Depends on all previous phases

### User Story 1 Internal Dependencies

1. **Schema updates (T002-T005)** - Must complete first (defines new types)
2. **Service layer (T006-T009)** - Depends on schema updates
3. **API routes (T010)** - Depends on schema updates
4. **All tests (T011-T026)** - Can run in parallel AFTER schema/service updates
5. **Validation (T027-T030)** - Must be last

### Parallel Opportunities Within User Story 1

**After Schema Updates Complete**:
```bash
# All test files can be updated in parallel:
T011-T016: Contract tests (test_agent_contract.py)
T017-T021: Integration tests (test_agent_api.py)
T022-T026: Unit tests (test_agent_orchestrator.py)

# Service and route updates can happen in parallel:
T006-T009: Service layer (react_agent.py)
T010: API routes (routes.py)
```

**User Story 2 Parallel Opportunities**:
```bash
# All documentation files can be updated in parallel:
T031-T032: README.md
T033: OpenAPI spec
```

---

## Implementation Strategy

### Sequential Approach (Single Developer)

1. **Phase 1**: Run baseline tests (T001)
2. **Phase 2**: Complete User Story 1 sequentially:
   - Schema updates (T002-T005)
   - Service layer (T006-T009)
   - API routes (T010)
   - Contract tests (T011-T016)
   - Integration tests (T017-T021)
   - Unit tests (T022-T026)
   - Validation (T027-T030)
3. **Phase 3**: Complete User Story 2 (T031-T035)
4. **Phase 4**: Final polish (T036-T039)

### Parallel Approach (If Desired)

1. **Phase 1**: Run baseline tests
2. **Phase 2**: After schema updates (T002-T005):
   - Launch T006-T010 (service/route updates) in parallel
   - Launch T011-T026 (all test updates) in parallel
   - Then validation (T027-T030)
3. **Phase 3**: Launch T031-T033 (all docs) in parallel, then T034-T035
4. **Phase 4**: Final validation

---

## Total Task Count

- **Phase 1 (Setup)**: 1 task
- **Phase 2 (User Story 1)**: 29 tasks
  - Schema/Service/Route: 9 tasks
  - Tests: 17 tasks
  - Validation: 4 tasks
- **Phase 3 (User Story 2)**: 5 tasks
- **Phase 4 (Polish)**: 4 tasks

**Total**: 39 tasks

---

## Notes

- This is a refactoring task - no new functionality, only field renaming
- All tasks maintain existing behavior - only names change
- Type safety via Pydantic and mypy ensures no references are missed
- [P] indicates tasks that can run in parallel (different files)
- Tests already exist - we're updating assertions, not writing new tests
- Each checkpoint provides an opportunity to validate independently
- MVP is just User Story 1 - code works with new field name
- User Story 2 (documentation) is important but not blocking for functionality
