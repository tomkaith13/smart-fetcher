# Tasks: Natural Language UUID Search

Feature: NL UUID Search (specs/004-nl-uuid-search/spec.md)
Date: 2025-12-27

## Phase 1: Setup

- [ ] T001 Establish feature branch naming and env vars in README.md
- [ ] T002 Add configuration for default results cap (5) in src/main.py
- [ ] T003 [P] Define `NLSearchResponse` and `ErrorResponse` examples in src/api/schemas.py
- [ ] T004 [P] Update OpenAPI with /nl/search in specs/004-nl-uuid-search/contracts/openapi.yaml
- [ ] T005 Add app state wiring for NL services in src/main.py
- [ ] T006 Verify health snapshot includes model name and resources in src/main.py

## Phase 2: Foundational

- [ ] T007 Implement `NLTagExtractor` using DSPy + Ollama in src/services/nl_tag_extractor.py
- [ ] T008 Implement `NLSearchService` orchestrating extract → map → verify → respond in src/services/nl_search_service.py
- [ ] T009 [P] Add deterministic link verifier in src/utils/link_verifier.py
- [ ] T010 [P] Extend `ResourceStore` helper: get_by_tags(list[str]) in src/services/resource_store.py
- [ ] T011 Add `ResourceItem` DTO (uuid, title, summary, link) in src/api/schemas.py
- [ ] T012 Configure graceful fallback to keyword extraction when inference unavailable in src/services/nl_tag_extractor.py

## Phase 3: User Story 1 (P1)

Goal: Ask in NL, get verified resources with internal deep links.

Independent Test Criteria:
- Provide query with known tag mappings; returns 3–5 `ResourceItem` entries, each with title, summary, and link `/resources/{uuid}`; all UUIDs resolve in `ResourceStore`.

Implementation Tasks

- [ ] T013 [US1] Add `GET /nl/search?q=` route to src/api/routes.py
- [ ] T014 [P] [US1] Validate `q` presence and maxLength=1000 in src/api/routes.py
- [ ] T015 [US1] Call `NLSearchService.search(q, cap=5)` in src/api/routes.py
- [ ] T016 [P] [US1] Assemble `NLSearchResponse` with `results/count/query` in src/api/routes.py
- [ ] T017 [US1] Implement `NLSearchService.search()` returning `ResourceItem[]` in src/services/nl_search_service.py
- [ ] T018 [P] [US1] Map extracted tags → UUIDs via `ResourceStore.get_by_tags()` in src/services/nl_search_service.py
- [ ] T019 [US1] Enforce result cap (default 5; configurable) in src/services/nl_search_service.py
- [ ] T020 [P] [US1] Verify each link via `link_verifier.resolve('/resources/{uuid}')` in src/services/nl_search_service.py

Tests (mandatory per spec)

- [ ] T021 [P] [US1] Contract: Add tests/contract/test_nl_search_responses.py
- [ ] T022 [P] [US1] Integration: Add tests/integration/test_nl_search_api.py
- [ ] T023 [P] [US1] Unit: Add tests/unit/test_nl_tag_extractor.py

## Phase 4: User Story 2 (P2)

Goal: Transparent handling of no-match queries (friendly response; no links).

Independent Test Criteria:
- Submit a query with no known tag mappings; response contains helpful message and at least two suggested tags; `count=0`; no links.

Implementation Tasks

- [ ] T024 [US2] Add no-match branch in `NLSearchService.search()` in src/services/nl_search_service.py
- [ ] T025 [P] [US2] Generate friendly NL message with suggestions in src/services/nl_search_service.py
- [ ] T026 [US2] Ensure `results=[]` and `count=0` in src/api/routes.py

Tests

- [ ] T027 [P] [US2] Contract: Validate schema and zero links in tests/contract/test_nl_search_responses.py
- [ ] T028 [P] [US2] Integration: No-match scenario path in tests/integration/test_nl_search_api.py

## Phase 5: User Story 3 (P3)

Goal: Ambiguity handling and refinement prompt with verified options.

Independent Test Criteria:
- Submit an ambiguous query; response presents 2–3 candidate tags with a refinement prompt; no fabricated links.

Implementation Tasks

- [ ] T029 [US3] Detect ambiguity via confidence distribution in src/services/nl_tag_extractor.py
- [ ] T030 [P] [US3] Return candidate tags list and prompt in src/services/nl_search_service.py
- [ ] T031 [US3] Ensure only verified options are listed in src/services/nl_search_service.py

Tests

- [ ] T032 [P] [US3] Contract: Candidate tags + prompt shape in tests/contract/test_nl_search_responses.py
- [ ] T033 [P] [US3] Integration: Ambiguity flow in tests/integration/test_nl_search_api.py

## Final Phase: Polish & Cross-Cutting

- [ ] T034 [P] Update docs: specs/004-nl-uuid-search/quickstart.md with NL example
- [ ] T035 [P] Add examples in README.md for `/nl/search`
- [ ] T036 Add ruff/mypy checks and fix types in src/**
- [ ] T037 [P] Add logging and tracing for tag extraction in src/services/nl_search_service.py
- [ ] T038 [P] Performance: cache available tags and avoid repeated model init in src/services/nl_tag_extractor.py
- [ ] T039 Ensure zero fabricated links; add omission logging in src/services/nl_search_service.py

## Dependencies

- US1 → US2 → US3
- Phase 1 → Phase 2 → US1 → US2 → US3 → Final Phase

## Parallel Execution Examples

- [P] Define schemas (T003, T011) while implementing services (T007–T010).
- [P] Route validation (T014) can proceed while service returns are stubbed (T017).
- [P] Tests (T021–T023) can be authored alongside endpoint scaffolding (T013–T016).
- [P] Ambiguity handling (T029–T031) can be developed while no-match paths (T024–T026) are verified.

## Implementation Strategy

- MVP: Complete US1 (T013–T023) with deterministic link verification; cap results at 5; fallback extraction if inference unavailable.
- Incremental: Add US2 no-match handling, then US3 ambiguity refinement; finalize documentation and performance polish.
