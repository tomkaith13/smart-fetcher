# Tasks: Natural Language UUID Search

Feature: NL UUID Search (specs/004-nl-uuid-search/spec.md)
Date: 2025-12-27

## Phase 1: Setup

- [X] T001 Establish feature branch naming and env vars in README.md
- [X] T002 Add configuration for default results cap (5) in src/main.py
- [X] T003 [P] Define `NLSearchResponse` and `ErrorResponse` examples in src/api/schemas.py
- [X] T004 [P] Update OpenAPI with /nl/search in specs/004-nl-uuid-search/contracts/openapi.yaml
- [X] T005 Add app state wiring for NL services in src/main.py
- [X] T006 Verify health snapshot includes model name and resources in src/main.py

## Phase 2: Foundational

- [X] T007 Implement `NLTagExtractor` using DSPy + Ollama in src/services/nl_tag_extractor.py
- [X] T007a Capture reasoning from DSPy extractor in `TagExtractionResult` in src/services/nl_tag_extractor.py
- [X] T008 Implement `NLSearchService` orchestrating extract → map → verify → respond in src/services/nl_search_service.py
- [X] T008a Remove per-item reasoning; include reasoning only at top-level `NLSearchResponse` and propagate through route/spec/tests/contracts
- [X] T009 [P] Add deterministic link verifier in src/utils/link_verifier.py
- [X] T010 [P] Extend `ResourceStore` helper: get_by_tags(list[str]) in src/services/resource_store.py
- [X] T011 Add `ResourceItem` DTO (uuid, title, summary, link) in src/api/schemas.py
- [X] T011a Add `reasoning` field to `NLSearchResponse` (top-level) in src/api/schemas.py
- [X] T012 Configure graceful fallback to keyword extraction when inference unavailable in src/services/nl_tag_extractor.py

## Phase 3: User Story 1 (P1)

Goal: Ask in NL, get verified resources with internal deep links.

Independent Test Criteria:
- Provide query with known tag mappings; returns 3–5 `ResourceItem` entries, each with title, summary, and link `/resources/{uuid}`; all UUIDs resolve in `ResourceStore`.

Implementation Tasks

- [X] T013 [US1] Add `GET /nl/search?q=` route to src/api/routes.py
- [X] T014 [P] [US1] Validate `q` presence and maxLength=1000 in src/api/routes.py
- [X] T015 [US1] Call `NLSearchService.search(q, cap=5)` in src/api/routes.py
- [X] T016 [P] [US1] Assemble `NLSearchResponse` with `results/count/query` in src/api/routes.py
- [X] T017 [US1] Implement `NLSearchService.search()` returning `ResourceItem[]` in src/services/nl_search_service.py
- [X] T018 [P] [US1] Map extracted tags → UUIDs via `ResourceStore.get_by_tags()` in src/services/nl_search_service.py
- [X] T019 [US1] Enforce result cap (default 5; configurable) in src/services/nl_search_service.py
- [X] T020 [P] [US1] Verify each link via `link_verifier.resolve('/resources/{uuid}')` in src/services/nl_search_service.py
- [X] T040 [P] [US1] Enforce `ResourceItem` fields in schemas and route: `uuid`, `name`, `summary`, `link` (`/resources/{uuid}`); server returns structured JSON only.

Tests (mandatory per spec)

- [X] T021 [P] [US1] Contract: Add tests/contract/test_nl_search_responses.py
- [X] T022 [P] [US1] Integration: Add tests/integration/test_nl_search_api.py
- [X] T023 [P] [US1] Unit: Add tests/unit/test_nl_tag_extractor.py
- [ ] T041 [P] [US1] Contract: Validate JSON wrapping (`results/count/query`), `count == len(results)`, and presence of `uuid`, `name`, `summary`, `link` fields.
- [ ] T042 [P] [US1] Integration: Assert only internal deep links `/resources/{uuid}` and confirm all returned UUIDs resolve in `ResourceStore`.

## Phase 4: User Story 2 (P2)

Goal: Transparent handling of no-match queries (friendly response; no links).

Independent Test Criteria:
- Submit a query with no known tag mappings; response contains helpful message and at least two suggested tags; `count=0`; no links.

Implementation Tasks

- [X] T024 [US2] Add no-match branch in `NLSearchService.search()` in src/services/nl_search_service.py
- [X] T025 [P] [US2] Generate friendly NL message with suggestions in src/services/nl_search_service.py
- [X] T026 [US2] Ensure `results=[]` and `count=0` in src/api/routes.py

Tests

- [X] T027 [P] [US2] Contract: Validate schema and zero links in tests/contract/test_nl_search_responses.py
- [X] T028 [P] [US2] Integration: No-match scenario path in tests/integration/test_nl_search_api.py

## Phase 5: User Story 3 (P3)

Goal: Ambiguity handling and refinement prompt with verified options.

Independent Test Criteria:
- Submit an ambiguous query; response presents 2–3 candidate tags with a refinement prompt; no fabricated links.

Implementation Tasks

- [X] T029 [US3] Detect ambiguity via confidence distribution in src/services/nl_tag_extractor.py
- [X] T030 [P] [US3] Return candidate tags list and prompt in src/services/nl_search_service.py
- [X] T031 [US3] Ensure only verified options are listed in src/services/nl_search_service.py

Tests

- [X] T032 [P] [US3] Contract: Candidate tags + prompt shape in tests/contract/test_nl_search_responses.py
- [X] T033 [P] [US3] Integration: Ambiguity flow in tests/integration/test_nl_search_api.py

## Final Phase: Polish & Cross-Cutting

- [X] T034 [P] Update docs: specs/004-nl-uuid-search/quickstart.md with NL example
- [X] T035 [P] Add examples in README.md for `/nl/search`
- [X] T036 Add ruff/mypy checks and fix types in src/**
- [X] T037 [P] Add logging and tracing for tag extraction in src/services/nl_search_service.py
- [X] T038 [P] Performance: cache available tags and avoid repeated model init in src/services/nl_tag_extractor.py
- [X] T039 Ensure zero fabricated links; add omission logging in src/services/nl_search_service.py
- [X] T043 [P] [FR-005] Regression: Run existing endpoint tests to verify `/search`, `/resources`, `/list`, `/health` unchanged
- [X] T044 [P] [FR-005] Regression: Validate existing API response schemas match pre-feature state
- [ ] T045 [P] Edge case: Add rate-limiting handling for inference (queue or friendly retry message)
- [ ] T046 [P] Edge case: Add test coverage for rate-limiting scenario

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
