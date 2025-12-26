# Phase 0: Research & Decisions

**Feature**: Expand Dataset for Semantic Search Testing  
**Date**: 2025-12-26  
**Status**: Complete

## Research Questions & Findings

### 1. Tag Distribution Algorithm

**Question**: How should we distribute 500 resources across 15 tags to ensure each tag has at least 40 entries with proportional distribution of the remainder?

**Research**:
- Current setup: 15 tags in TAG_CATEGORIES list
- Requirement: Minimum 40 per tag = 600 total minimum (exceeds 500!)
- **Issue Identified**: With 15 tags requiring 40 each, we need 600 resources minimum, but spec says 500 total

**Decision**: 
- **Tag count must be reduced** OR **target count must be increased** to meet 40-per-tag requirement
- With 500 resources and 40 minimum per tag: Maximum 12 tags supported (12 × 40 = 480, leaving 20 for proportional distribution)
- **Recommended approach**: Use only 12 of the 15 existing tags, distributing the 20 remaining resources proportionally based on original distribution in the 100-resource baseline

**Distribution Algorithm**:
```
1. Select 12 tags from the existing 15 (keep most commonly used)
2. Assign 40 base resources to each tag (480 total)
3. Distribute remaining 20 resources proportionally based on original frequency
4. Formula: extra[tag] = round(original_frequency[tag] × 20)
```

**Alternative Considered**: Increase total to 600 resources to support all 15 tags.
**Rejected Because**: Spec explicitly states 500 resources as success criterion (SC-001).

---

### 2. Contextual Content Generation Strategy

**Question**: How can we generate contextually appropriate content for each tag using the existing Faker library without adding new dependencies?

**Research**:
- Faker provides semantic generators: `fake.catch_phrase()`, `fake.paragraph()`, `fake.bs()`, `fake.company()`
- Current implementation: Random catch phrases and paragraphs (no tag context)
- Faker limitation: No built-in tag-specific content generation

**Decision**:
- Create tag-specific content templates using Faker's building blocks
- Each tag category maps to a set of Faker method combinations
- Examples:
  - `home`: Use `fake.street_address()`, `fake.building_number()`, `fake.city()` in descriptions
  - `car`: Use `fake.color()`, `fake.word()` + vehicle terms, model names
  - `technology`: Use `fake.bs()` (business speak), tech buzzwords
  - `health`: Use medical/wellness vocabulary + `fake.paragraph()`

**Implementation Pattern**:
```python
TAG_CONTENT_GENERATORS = {
    "home": lambda fake: {
        "name": f"{fake.street_name()} {random.choice(['House', 'Residence', 'Property'])}",
        "description": f"Located at {fake.address()}. Features {fake.catch_phrase()}."
    },
    # ... more tag-specific generators
}
```

**Alternative Considered**: Use LLM to generate contextual content.
**Rejected Because**: Violates "no new dependencies" constraint, introduces non-determinism, slow generation time.

---

### 3. Deterministic Generation with Increased Count

**Question**: How do we maintain deterministic generation when scaling from 100 to 500 resources while preserving the original 100?

**Research**:
- Current approach: `random.seed(SEED)`, `Faker.seed(SEED)` at start of generation
- Seeded random produces deterministic sequence
- Concern: Changing count changes the UUID sequence for all resources

**Decision**:
- **Break compatibility** - regenerate all 500 resources with new distribution
- Rationale: Test data consistency less important than meeting new requirements (40+ per tag)
- Document in migration notes that UUIDs will change

**Alternative Considered**: Generate 400 new resources, append to existing 100.
**Rejected Because**: 
1. Original 100 likely don't meet 40-per-tag requirement
2. Distribution would be unbalanced (old random + new structured)
3. Complexity of merging two generation approaches

---

### 4. Validation Strategy

**Question**: What validation logic is needed to verify dataset integrity per FR-005 and FR-006?

**Research**:
- Requirements to validate:
  1. Total count = 500 (FR-001)
  2. Each tag ≥ 40 entries (FR-002)
  3. Unique UUIDs (FR-008)
  4. Single tag per resource (FR-005)
  5. Valid Resource schema (FR-004)
  6. Tags from existing vocabulary (FR-009)

**Decision**:
Create `dataset_validator.py` utility module with functions:
- `validate_total_count(resources, expected=500) -> bool`
- `validate_tag_distribution(resources, min_per_tag=40) -> dict[str, int]`
- `validate_unique_uuids(resources) -> bool`
- `validate_single_tags(resources) -> bool`
- `validate_schemas(resources) -> bool`
- `validate_comprehensive(resources) -> ValidationReport` (combines all)

Return structured results:
```python
@dataclass
class ValidationReport:
    total_count: tuple[bool, int, int]  # (pass, actual, expected)
    tag_distribution: dict[str, tuple[bool, int]]  # tag -> (pass, count)
    unique_uuids: bool
    single_tags: bool
    schema_valid: bool
    overall_pass: bool
```

**Alternative Considered**: Use pytest assertions directly in tests.
**Rejected Because**: Validation logic useful for manual checks, CI scripts, future tooling.

---

### 5. Backward Compatibility Concerns

**Question**: Will changing from 100 to 500 resources break existing tests or API responses?

**Research**:
- ResourceStore API: No count assumptions in interface
- Test fixtures: Some tests may hardcode count=100 assumptions
- API responses: Return actual resources, no hardcoded expectations
- Semantic search: Context size increases (100 → 500 resources in LLM prompt)

**Decision**:
- Update test fixtures to use new 500-resource baseline
- Add configuration parameter to `generate_resources(count: int = 500)` for flexibility
- Document context size increase in quickstart (may affect LLM inference time)
- Tests that check specific counts must be updated

**Breaking Changes**:
1. ✅ ResourceStore default count changes (100 → 500)
2. ✅ UUIDs change (complete regeneration)
3. ✅ Tag distribution changes (structured vs random)

**Migration Path**:
- Update tests to assert `>= 40` per tag instead of exact counts
- Regenerate test fixtures with new seed
- Performance test with 500-resource context size

---

## Technology Decisions

### Dependencies

**No new dependencies added** - constraint met.

Using existing:
- `faker>=33.0.0` - synthetic data generation
- `pydantic>=2.10.0` - schema validation
- `pytest>=8.3.0` - testing framework

### Testing Approach

**Unit Tests** (`tests/unit/test_dataset_validator.py`):
- Test each validation function independently
- Mock resources with known properties
- Verify edge cases (exactly 40, 0 resources, duplicate UUIDs)

**Contract Tests** (`tests/contract/test_resource_responses.py`):
- Verify expanded dataset matches Resource schema
- Check 500 resources returned from API
- Validate tag distribution in responses

**Integration Tests** (existing `tests/integration/test_search_api.py`):
- May benefit from larger dataset (more semantic variety)
- Performance baseline with 500 resources
- No changes required (tests remain valid)

### Performance Considerations

**Generation Time**:
- Current: 100 resources in ~10ms
- Expected: 500 resources in ~50ms (linear scaling)
- Acceptable: <1 second per spec

**Context Size for LLM**:
- Current: 100 resources × ~50 bytes = ~5KB context
- New: 500 resources × ~50 bytes = ~25KB context
- Impact: Minimal (well within Ollama context limits)

---

## Open Questions

**None remaining** - all clarifications resolved during `/speckit.clarify` phase.

---

## Next Phase

Proceed to Phase 1: Data Model and Contracts generation.
