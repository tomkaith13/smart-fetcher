# Tasks: Smart Tag-Based Resource Fetcher

**Input**: Design documents from `/specs/001-dspy-tag-fetcher/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Included per constitution requirement (80% coverage target)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Create project structure: `src/`, `src/models/`, `src/services/`, `src/api/`, `tests/`, `tests/unit/`, `tests/integration/`, `tests/contract/`
- [x] T002 Add runtime dependencies to pyproject.toml: fastapi, uvicorn, pydantic, dspy, faker
- [x] T003 [P] Add dev dependencies to pyproject.toml: pytest, pytest-cov, pytest-asyncio, ruff, mypy, httpx
- [x] T004 [P] Create `src/__init__.py`, `src/models/__init__.py`, `src/services/__init__.py`, `src/api/__init__.py`
- [x] T005 [P] Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/contract/__init__.py`
- [x] T006 [P] Configure ruff in pyproject.toml (linting + formatting rules)
- [x] T007 [P] Configure mypy in pyproject.toml (strict type checking)
- [x] T008 Run `uv sync` to install all dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Create Resource Pydantic model in `src/models/resource.py` with uuid, name, description, search_tag fields per data-model.md
- [x] T010 [P] Create response schemas in `src/api/schemas.py`: SearchResponse, ResourceResponse, ListResponse, ErrorResponse, HealthResponse per data-model.md
- [x] T011 Create TAG_CATEGORIES list (15 categories) in `src/services/resource_store.py` per research.md
- [x] T012 Implement `generate_resources()` function in `src/services/resource_store.py` using Faker + random.seed(42) to create 100 deterministic resources
- [x] T013 Implement ResourceStore class in `src/services/resource_store.py` with `_resources` dict, `_tags_to_uuids` index, and `get_by_uuid()`, `get_all()`, `get_unique_tags()` methods
- [x] T014 Create shared test fixtures in `tests/conftest.py`: sample resources, mock Ollama client, test client for FastAPI
- [x] T015 Create FastAPI app skeleton in `src/main.py` with lifespan handler to initialize ResourceStore on startup

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Search Resources by Tag (Priority: P1) 🎯 MVP

**Goal**: Users can search for resources using a semantic tag and receive all semantically related resources (including synonyms)

**Independent Test**: Send `GET /search?tag=home` and verify resources with related tags (home, house, residence, dwelling) are returned in wrapped JSON format

### Tests for User Story 1

- [x] T016 [P] [US1] Unit test for SemanticResourceFinder signature in `tests/unit/test_semantic_search.py` - mock LLM, verify tag matching logic
- [x] T017 [P] [US1] Contract test for /search endpoint in `tests/contract/test_search_responses.py` - verify SearchResponse and ErrorResponse formats match OpenAPI spec
- [x] T018 [P] [US1] Integration test for search flow in `tests/integration/test_search_api.py` - test empty tag, valid tag, no matches, service unavailable scenarios

### Implementation for User Story 1

- [x] T019 [US1] Create SemanticResourceFinder DSPy Signature in `src/services/semantic_search.py` with search_tag, resources_context inputs and matching_uuids output per research.md
- [x] T020 [US1] Implement SemanticSearchService class in `src/services/semantic_search.py` using dspy.ChainOfThought(SemanticResourceFinder), with `find_matching(tag)` method
- [x] T021 [US1] Configure DSPy LM with Ollama in `src/services/semantic_search.py`: `dspy.LM("ollama_chat/gpt-oss:20b", api_base="http://localhost:11434")`
- [x] T022 [US1] Implement `GET /search` endpoint in `src/api/routes.py` with tag query parameter, input validation (MISSING_TAG, TAG_TOO_LONG), and SearchResponse return
- [x] T023 [US1] Add error handling for Ollama unavailability (SERVICE_UNAVAILABLE) in `src/api/routes.py`
- [x] T024 [US1] Wire SemanticSearchService to FastAPI app in `src/main.py` via lifespan dependency injection

**Checkpoint**: User Story 1 complete - semantic search should work end-to-end

---

## Phase 4: User Story 2 - Retrieve Resource by UUID (Priority: P2)

**Goal**: Users can fetch a specific resource by its unique identifier after discovering it via search

**Independent Test**: Send `GET /resources/{uuid}` with a known UUID and verify the complete resource object is returned

### Tests for User Story 2

- [x] T025 [P] [US2] Unit test for ResourceStore.get_by_uuid() in `tests/unit/test_resource_store.py` - verify O(1) lookup, return None for missing UUID
- [x] T026 [P] [US2] Contract test for /resources/{uuid} endpoint in `tests/contract/test_resource_responses.py` - verify ResourceResponse and ErrorResponse (RESOURCE_NOT_FOUND, INVALID_UUID) formats
- [x] T027 [P] [US2] Integration test for UUID lookup in `tests/integration/test_resource_api.py` - test valid UUID, invalid format, not found scenarios

### Implementation for User Story 2

- [x] T028 [US2] Implement `GET /resources/{uuid}` endpoint in `src/api/routes.py` with UUID path parameter validation and ResourceResponse return
- [x] T029 [US2] Add error handling for INVALID_UUID (malformed) and RESOURCE_NOT_FOUND (missing) in `src/api/routes.py`

**Checkpoint**: User Story 2 complete - UUID lookup should work independently

---

## Phase 5: User Story 3 - List All Resources (Priority: P3)

**Goal**: Users can browse the complete catalog of all 100 resources

**Independent Test**: Send `GET /resources` and verify all 100 resources are returned with count field

### Tests for User Story 3

- [x] T030 [P] [US3] Contract test for /resources endpoint in `tests/contract/test_list_responses.py` - verify ListResponse format with resources array and count
- [x] T031 [P] [US3] Integration test for list all in `tests/integration/test_list_api.py` - verify 100 resources returned, correct structure

### Implementation for User Story 3

- [x] T032 [US3] Implement `GET /resources` endpoint in `src/api/routes.py` returning ListResponse with all resources and count

**Checkpoint**: User Story 3 complete - list all should return 100 resources

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Health check, quality gates, and final validation

- [x] T033 Implement `GET /health` endpoint in `src/api/routes.py` checking Ollama connectivity and resources_loaded count
- [x] T034 [P] Add docstrings to all public functions and classes per constitution requirements
- [x] T035 [P] Run `uv run ruff check .` and fix any linting errors
- [x] T036 [P] Run `uv run ruff format .` to format all code
- [ ] T037 Run `uv run mypy src/` and fix any type errors (SKIPPED by user)
- [x] T038 Run `uv run pytest --cov=src --cov-report=term-missing` and verify ≥80% coverage
- [ ] T039 Validate quickstart.md instructions work end-to-end (manual smoke test)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────► Phase 2 (Foundational) ──┬──► Phase 3 (US1: Search) ───┐
                                                  ├──► Phase 4 (US2: UUID)    ──┼──► Phase 6 (Polish)
                                                  └──► Phase 5 (US3: List)   ───┘
```

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-5)**: All depend on Foundational; can run in parallel after Phase 2
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Can Start After | Independent Test |
|-------|------------|-----------------|------------------|
| US1 (Search) | Foundational | T015 | `curl /search?tag=home` |
| US2 (UUID Lookup) | Foundational | T015 | `curl /resources/{uuid}` |
| US3 (List All) | Foundational | T015 | `curl /resources` |

### Within Each User Story

1. Tests written first (should FAIL before implementation)
2. Core service logic implemented
3. API endpoint implemented
4. Error handling added
5. Story complete and independently testable

### Parallel Opportunities

**Phase 1 parallel group:**
```
T003, T004, T005, T006, T007 (all independent setup tasks)
```

**Phase 2 parallel group:**
```
T010 (schemas) can run parallel with T009 (model)
```

**Phase 3 US1 tests (parallel):**
```
T016, T017, T018 (all test files independent)
```

**Phase 4 US2 tests (parallel):**
```
T025, T026, T027 (all test files independent)
```

**Phase 5 US3 tests (parallel):**
```
T030, T031 (all test files independent)
```

**Phase 6 parallel group:**
```
T034, T035, T036 (independent quality tasks)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T015)
3. Complete Phase 3: User Story 1 - Search (T016-T024)
4. **STOP and VALIDATE**: Test `GET /search?tag=home` works
5. Deploy/demo semantic search capability

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Search) → Test → Deploy (MVP!)
3. Add US2 (UUID Lookup) → Test → Deploy
4. Add US3 (List All) → Test → Deploy
5. Add Polish → Run quality gates → Final release

---

## Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Phase 1: Setup | T001-T008 (8 tasks) | T003-T007 (5 parallel) |
| Phase 2: Foundational | T009-T015 (7 tasks) | T010 with T009 |
| Phase 3: US1 Search | T016-T024 (9 tasks) | T016-T018 (3 parallel tests) |
| Phase 4: US2 UUID | T025-T029 (5 tasks) | T025-T027 (3 parallel tests) |
| Phase 5: US3 List | T030-T032 (3 tasks) | T030-T031 (2 parallel tests) |
| Phase 6: Polish | T033-T039 (7 tasks) | T034-T036 (3 parallel) |
| **Total** | **39 tasks** | **16 parallelizable** |

---

## Notes

- All [P] tasks can run in parallel (different files, no dependencies)
- [Story] labels enable filtering tasks by user story
- Each user story is independently testable after completion
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
