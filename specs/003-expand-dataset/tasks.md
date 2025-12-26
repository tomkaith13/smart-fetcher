---
description: "Implementation tasks for dataset expansion feature"
---

# Tasks: Expand Dataset for Semantic Search Testing

**Input**: Design documents from `/specs/003-expand-dataset/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: NOT REQUESTED - This feature does not require new test creation as it's enhancing existing test data infrastructure

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification of existing structure

- [X] T001 Verify existing project structure matches plan.md (src/models/, src/services/, src/utils/, tests/)
- [X] T002 [P] Verify Faker, Pydantic, and pytest dependencies are installed per pyproject.toml
- [X] T003 [P] Review TAG_CATEGORIES list in src/services/resource_store.py to identify 12 most common tags

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Utilities and models needed by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create src/utils/ directory if it doesn't exist
- [X] T005 [P] Create ValidationReport Pydantic model in src/utils/dataset_validator.py with all attributes (total_count_pass, actual_count, expected_count, tag_distribution, unique_uuids, single_tags, schema_valid, overall_pass)
- [X] T006 [P] Implement ValidationReport.summary() method in src/utils/dataset_validator.py to generate human-readable output
- [X] T007 Create tag content generator type alias and structure in src/services/resource_store.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Comprehensive Tag Coverage Testing (Priority: P1) 🎯 MVP

**Goal**: Expand dataset to 500 resources with minimum 40 entries per tag, enabling thorough semantic search testing across all categories

**Independent Test**: Load expanded dataset, verify total count = 500, verify each of 12 tags has ≥40 entries, confirm all resources searchable

### Implementation for User Story 1

- [X] T008 [P] [US1] Create tag-specific content generator for "home" tag in src/services/resource_store.py using Faker methods (fake.street_name(), fake.address(), fake.catch_phrase())
- [X] T009 [P] [US1] Create tag-specific content generator for "car" tag in src/services/resource_store.py using Faker methods (fake.color(), vehicle terms, fake.company(), fake.bs())
- [X] T010 [P] [US1] Create tag-specific content generator for "technology" tag in src/services/resource_store.py using Faker methods (fake.bs(), tech buzzwords, fake.catch_phrase())
- [X] T011 [P] [US1] Create tag-specific content generator for "food" tag in src/services/resource_store.py using Faker methods (fake.word(), food terms, fake.sentence())
- [X] T012 [P] [US1] Create tag-specific content generator for "health" tag in src/services/resource_store.py using Faker methods (medical vocabulary, fake.paragraph())
- [X] T013 [P] [US1] Create tag-specific content generator for "finance" tag in src/services/resource_store.py using Faker methods (fake.company(), financial terms, fake.bs())
- [X] T014 [P] [US1] Create tag-specific content generator for "travel" tag in src/services/resource_store.py using Faker methods (fake.city(), fake.country(), fake.catch_phrase())
- [X] T015 [P] [US1] Create tag-specific content generator for "education" tag in src/services/resource_store.py using Faker methods (academic terms, fake.job(), fake.sentence())
- [X] T016 [P] [US1] Create tag-specific content generator for "sports" tag in src/services/resource_store.py using Faker methods (sports terms, fake.word(), fake.sentence())
- [X] T017 [P] [US1] Create tag-specific content generator for "music" tag in src/services/resource_store.py using Faker methods (music terms, fake.word(), fake.catch_phrase())
- [X] T018 [P] [US1] Create tag-specific content generator for "fashion" tag in src/services/resource_store.py using Faker methods (fake.color(), fashion terms, fake.sentence())
- [X] T019 [P] [US1] Create tag-specific content generator for "nature" tag in src/services/resource_store.py using Faker methods (nature terms, fake.sentence(), fake.paragraph())
- [X] T020 [US1] Create TAG_CONTENT_GENERATORS dictionary in src/services/resource_store.py mapping all 12 selected tags to their generator functions (depends on T008-T019)
- [X] T021 [US1] Implement tag selection logic in generate_resources() to select 12 most common tags from TAG_CATEGORIES in src/services/resource_store.py
- [X] T022 [US1] Implement tag distribution algorithm in generate_resources() to assign base count of 40 per tag (480 total) in src/services/resource_store.py
- [X] T023 [US1] Implement proportional remainder distribution logic for remaining 20 resources in generate_resources() in src/services/resource_store.py
- [X] T024 [US1] Update generate_resources() signature to accept count parameter (default=500) and seed parameter in src/services/resource_store.py
- [X] T025 [US1] Update resource generation loop in generate_resources() to use tag-specific content generators instead of generic fake.catch_phrase() in src/services/resource_store.py
- [X] T026 [US1] Ensure deterministic generation by properly seeding random and Faker at start of generate_resources() in src/services/resource_store.py
- [X] T027 [US1] Update ResourceStore.__init__() default to call generate_resources(count=500) instead of 100 in src/services/resource_store.py
- [X] T028 [P] [US1] Update test assertions in tests/unit/test_resource_store.py to expect 500 resources instead of 100
- [X] T029 [P] [US1] Add new test in tests/unit/test_resource_store.py to verify each tag has at least 40 entries
- [X] T030 [P] [US1] Update test fixtures in tests/contract/test_resource_responses.py to work with 500-resource dataset
- [X] T031 [P] [US1] Update test fixtures in tests/contract/test_list_responses.py to expect count=500 in API responses

**Checkpoint**: At this point, User Story 1 should be fully functional - dataset expanded to 500 resources with proper tag distribution

---

## Phase 4: User Story 2 - Diverse Semantic Relationship Testing (Priority: P2)

**Goal**: Ensure tag-specific content generators produce contextually appropriate and varied content for meaningful semantic search validation

**Independent Test**: Generate dataset, manually inspect 5-10 resources per tag category to verify contextual appropriateness, perform synonym searches (e.g., "automobile" → "car" tags) and measure recall

### Implementation for User Story 2

- [X] T032 [P] [US2] Implement validate_unique_uuids() function in src/utils/dataset_validator.py to check all UUIDs are unique
- [X] T033 [P] [US2] Implement validate_single_tags() function in src/utils/dataset_validator.py to verify each resource has exactly one tag
- [X] T034 [P] [US2] Implement validate_schemas() function in src/utils/dataset_validator.py to verify all resources match Resource Pydantic model
- [X] T035 [US2] Review and enhance content generators in src/services/resource_store.py to ensure sufficient semantic variety within each tag (at least 3-4 different patterns per tag)
- [X] T036 [US2] Test semantic search quality by running sample queries against expanded dataset and verifying synonym matching works correctly
- [X] T037 [P] [US2] Update integration tests in tests/integration/test_search_api.py to include semantic similarity test cases (e.g., "house" should return "home" tagged resources)
- [X] T038-OPT [US2] Optimize semantic search for scale: Refactor SemanticSearchService to use tag classification approach instead of UUID selection (classify search tag → best matching tag → O(1) resource lookup via tag index)
  - Update SemanticResourceFinder signature to take search_tag + available_tags (12 tags) → best_matching_tag
  - Create signature dynamically with actual tags embedded in field descriptions
  - Add ResourceStore.get_by_tag() method for O(1) tag-based lookup
  - Update SemanticSearchService.find_matching() to use two-step process
  - Update tests in tests/unit/test_semantic_search.py to mock best_matching_tag instead of matching_uuids
  - Add tests for ResourceStore.get_by_tag() in tests/unit/test_resource_store.py
  - Benefits: 97% context reduction (500 resources → 12 tags), simpler LLM task, faster inference

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - dataset has proper size AND semantic quality, with optimized semantic search at scale

---

## Phase 5: User Story 3 - Performance and Scalability Baseline (Priority: P3)

**Goal**: Validate that expanded dataset performs acceptably and establish performance baselines for future capacity planning

**Independent Test**: Run standardized search queries against 500-resource dataset, measure response times and memory usage, compare against 100-resource baseline (should be within 2x)

### Implementation for User Story 3

- [X] T038 [P] [US3] Implement validate_total_count() function in src/utils/dataset_validator.py to verify exact resource count matches expected (500)
- [X] T039 [P] [US3] Implement validate_tag_distribution() function in src/utils/dataset_validator.py to check each tag has minimum required entries (40)
- [X] T040 [US3] Implement validate_comprehensive() function in src/utils/dataset_validator.py that combines all validation checks and returns ValidationReport (depends on T005, T032-T034, T038-T039)
- [X] T041 [US3] Create simple performance test script (can be temporary in tests/ or root) to measure dataset generation time and verify <1 second requirement
- [X] T042 [US3] Measure and document search API response time baseline with 500 resources compared to previous 100-resource baseline
- [X] T043 [P] [US3] Create tests/unit/test_dataset_validator.py with tests for each validation function (validate_total_count, validate_tag_distribution, validate_unique_uuids, validate_single_tags, validate_schemas)
- [X] T044 [P] [US3] Add comprehensive validation test in tests/unit/test_dataset_validator.py that verifies validate_comprehensive() correctly aggregates all checks

**Checkpoint**: All user stories should now be independently functional - dataset is expanded, semantically rich, and validated with performance baselines

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [X] T045 [P] Update README.md to document expanded dataset (500 resources, 12 tags, 40+ per tag)
- [X] T046 [P] Add docstrings to all new functions in src/utils/dataset_validator.py following existing project style
- [X] T047 [P] Add docstrings to updated generate_resources() function in src/services/resource_store.py
- [X] T048 [P] Add type hints to all new validation functions in src/utils/dataset_validator.py
- [X] T049 Run ruff check and ruff format on all modified files (src/services/resource_store.py, src/utils/dataset_validator.py, test files)
- [X] T050 Run mypy type checking on all modified files to ensure type safety
- [X] T051 Execute full test suite (pytest) to verify all tests pass with expanded dataset
- [X] T052 Run validation from quickstart.md Section 4 to verify manual testing scenarios work correctly
- [X] T053 Generate ValidationReport for final dataset and save output for documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1) is MVP and should be completed first
  - User Story 2 (P2) can proceed in parallel with US1 once foundational is done, but builds on US1's generators
  - User Story 3 (P3) depends on US1's dataset expansion being complete for performance testing
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - THIS IS MVP
- **User Story 2 (P2)**: Can start after US1 generators exist (T020), enhances content quality - Independently testable by inspecting generated content
- **User Story 3 (P3)**: Depends on US1 completion (needs 500-resource dataset to measure performance) - Independently testable by running performance benchmarks

### Within Each User Story

- **US1**: Content generators (T008-T019) can be written in parallel → TAG_CONTENT_GENERATORS dict (T020) → Distribution logic (T021-T023) → Update generation function (T024-T027) → Update tests (T028-T031)
- **US2**: Validation functions (T032-T034) can be written in parallel → Content review (T035) → Semantic testing (T036-T037)
- **US3**: Validation functions (T038-T039) can be written in parallel → Comprehensive validator (T040) → Performance tests (T041-T042) → Unit tests (T043-T044)

### Parallel Opportunities

- **Setup Phase**: Tasks T002 and T003 can run in parallel
- **Foundational Phase**: Tasks T005 and T006 can run in parallel with T007
- **User Story 1**: 
  - All content generator tasks (T008-T019) can run in parallel - 12 independent generators
  - Test update tasks (T028-T031) can run in parallel after implementation complete
- **User Story 2**:
  - Validation functions (T032-T034) can be written in parallel
  - Test update (T037) can run in parallel with content review (T035-T036)
- **User Story 3**:
  - Validation functions (T038-T039) can run in parallel
  - Unit tests (T043-T044) can be written in parallel
- **Polish Phase**: Documentation tasks (T045-T048) can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all content generators together (12 parallel tasks):
Task T008: "Create tag-specific content generator for 'home' tag"
Task T009: "Create tag-specific content generator for 'car' tag"
Task T010: "Create tag-specific content generator for 'technology' tag"
Task T011: "Create tag-specific content generator for 'food' tag"
Task T012: "Create tag-specific content generator for 'health' tag"
Task T013: "Create tag-specific content generator for 'finance' tag"
Task T014: "Create tag-specific content generator for 'travel' tag"
Task T015: "Create tag-specific content generator for 'education' tag"
Task T016: "Create tag-specific content generator for 'sports' tag"
Task T017: "Create tag-specific content generator for 'music' tag"
Task T018: "Create tag-specific content generator for 'fashion' tag"
Task T019: "Create tag-specific content generator for 'nature' tag"

# After generators complete, launch all test updates together:
Task T028: "Update test assertions in tests/unit/test_resource_store.py"
Task T029: "Add tag distribution test in tests/unit/test_resource_store.py"
Task T030: "Update test fixtures in tests/contract/test_resource_responses.py"
Task T031: "Update test fixtures in tests/contract/test_list_responses.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → Verify existing structure
2. Complete Phase 2: Foundational → Create ValidationReport model and generator structure
3. Complete Phase 3: User Story 1 → Expand dataset to 500 with proper distribution
4. **STOP and VALIDATE**: Run generate_resources(500), verify count and tag distribution
5. This is the MVP - expanded dataset ready for comprehensive testing

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (T008-T031) → Test independently → **MVP READY** (500 resources, proper distribution)
3. Add User Story 2 (T032-T037) → Test independently → Enhanced semantic quality
4. Add User Story 3 (T038-T044) → Test independently → Performance validated and baseline established
5. Polish (T045-T053) → Documentation and final validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Create 12 content generators in parallel (T008-T019)
   - Developer B: Start on validation functions (T032-T034, T038-T039)
   - Developer C: Prepare test infrastructure updates
3. Developer A completes US1 implementation (T020-T027)
4. All developers update tests in parallel (T028-T031, T037, T043-T044)

---

## Notes

- **No test creation required**: This feature enhances test data infrastructure. Existing tests are updated to work with expanded dataset.
- **MVP is User Story 1**: Delivers immediate value by providing 500-resource dataset for semantic search testing
- **12 tags, not 15**: Research revealed that 500 resources with 40 minimum per tag supports maximum 12 tags (12×40=480, plus 20 remainder)
- **Deterministic generation**: All generation uses fixed seed for reproducibility
- **Backward compatibility**: ResourceStore API unchanged, only default count increases
- [P] tasks = different files or independent functions, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently

---

## Success Criteria Validation

After completing all tasks, verify these success criteria from spec.md:

- **SC-001**: ✅ Resource store contains exactly 500 resources (verify with validate_total_count)
- **SC-002**: ✅ 100% of 12 selected tags have at least 40 associated resources (verify with validate_tag_distribution)
- **SC-003**: ✅ Semantic search queries return results within 3 seconds for 95% of queries (baseline in US3)
- **SC-004**: ✅ QA team can execute 50+ distinct semantic search test cases across all tag categories
- **SC-005**: ✅ Data validation tests pass with 100% success rate (validate_comprehensive returns overall_pass=True)
- **SC-006**: ✅ Semantic search precision remains at or above baseline (test in US2)
