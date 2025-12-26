# Quickstart: Dataset Expansion Implementation

**Feature**: Expand Dataset from 100 to 500 Resources  
**Branch**: `003-expand-dataset`  
**Estimated Time**: 2-3 hours

## Overview

This guide walks through implementing the dataset expansion feature, which increases the test dataset from 100 to 500 resources with strict single-tag categorization and minimum 40 entries per tag.

## Prerequisites

- Python 3.13+ installed
- Existing smart-fetcher repository cloned
- Dependencies installed: `pip install -e ".[dev]"`
- Familiarity with Faker library and Pydantic models

## Implementation Steps

### Step 1: Update Resource Generation Logic (45 min)

**File**: `src/services/resource_store.py`

**Tasks**:
1. Update `generate_resources()` signature to support 500 count
2. Implement tag selection (reduce from 15 to 12 tags)
3. Add tag distribution algorithm (40 base + proportional remainder)
4. Create tag-specific content generators
5. Update generation loop to use contextual content

**Key Changes**:

```python
# Add tag-specific content generators
TAG_CONTENT_GENERATORS = {
    "home": lambda fake: {
        "name": f"{fake.street_name()} {random.choice(['House', 'Residence', 'Property'])}",
        "description": f"Located at {fake.address()}. Features {fake.catch_phrase()}."
    },
    "car": lambda fake: {
        "name": f"{fake.color()} {random.choice(['Sedan', 'SUV', 'Coupe', 'Truck'])}",
        "description": f"{fake.company()} vehicle with {fake.bs()} technology."
    },
    # Add generators for 10 more tags
}

# Update function signature
def generate_resources(count: int = 500, seed: int = SEED) -> list[Resource]:
    """Generate deterministic resources with contextual content per tag."""
    random.seed(seed)
    Faker.seed(seed)
    fake = Faker()
    
    # Calculate distribution (12 tags × 40 base = 480, remainder 20)
    selected_tags = TAG_CATEGORIES[:12]  # Use first 12 tags
    distribution = {tag: 40 for tag in selected_tags}
    
    # Distribute remainder proportionally
    remainder = count - (len(selected_tags) * 40)
    # ... proportional distribution logic ...
    
    resources = []
    for tag, tag_count in distribution.items():
        generator = TAG_CONTENT_GENERATORS[tag]
        for _ in range(tag_count):
            content = generator(fake)
            resources.append(Resource(
                uuid=str(uuid_lib.UUID(int=random.getrandbits(128))),
                name=content["name"],
                description=content["description"],
                search_tag=tag
            ))
    
    return resources
```

**Verification**:
```bash
# In Python REPL
from src.services.resource_store import generate_resources
resources = generate_resources(500)
assert len(resources) == 500
assert all(r.search_tag in TAG_CATEGORIES[:12] for r in resources)
```

---

### Step 2: Create Validation Utilities (30 min)

**File**: `src/utils/dataset_validator.py` (new file)

**Tasks**:
1. Create ValidationReport Pydantic model
2. Implement `validate_total_count()`
3. Implement `validate_tag_distribution()`
4. Implement `validate_unique_uuids()`
5. Implement `validate_single_tags()`
6. Implement `validate_schemas()`
7. Create comprehensive validator combining all checks

**Example Implementation**:

```python
from pydantic import BaseModel
from src.models.resource import Resource

class ValidationReport(BaseModel):
    total_count_pass: bool
    actual_count: int
    expected_count: int
    tag_distribution: dict[str, tuple[bool, int]]
    unique_uuids: bool
    single_tags: bool
    schema_valid: bool
    overall_pass: bool

def validate_comprehensive(resources: list[Resource], 
                          expected_count: int = 500,
                          min_per_tag: int = 40) -> ValidationReport:
    """Run all validation checks and return comprehensive report."""
    # Validate counts
    total_pass = len(resources) == expected_count
    
    # Validate tag distribution
    tag_counts = {}
    for r in resources:
        tag_counts[r.search_tag] = tag_counts.get(r.search_tag, 0) + 1
    
    tag_dist = {
        tag: (count >= min_per_tag, count) 
        for tag, count in tag_counts.items()
    }
    
    # Validate unique UUIDs
    uuids = [r.uuid for r in resources]
    unique_pass = len(uuids) == len(set(uuids))
    
    # Validate single tags (already enforced by schema)
    single_tags_pass = all(isinstance(r.search_tag, str) for r in resources)
    
    # Validate schemas
    schema_pass = all(isinstance(r, Resource) for r in resources)
    
    overall = (total_pass and unique_pass and single_tags_pass and 
               schema_pass and all(p for p, _ in tag_dist.values()))
    
    return ValidationReport(
        total_count_pass=total_pass,
        actual_count=len(resources),
        expected_count=expected_count,
        tag_distribution=tag_dist,
        unique_uuids=unique_pass,
        single_tags=single_tags_pass,
        schema_valid=schema_pass,
        overall_pass=overall
    )
```

**Verification**:
```bash
from src.utils.dataset_validator import validate_comprehensive
report = validate_comprehensive(resources)
print(report.summary())
# Should show all checks passing
```

---

### Step 3: Update Tests (45 min)

**Files to Update**:
- `tests/unit/test_resource_store.py`
- `tests/contract/test_resource_responses.py`
- `tests/contract/test_list_responses.py`

**New File**:
- `tests/unit/test_dataset_validator.py`

**Key Updates**:

```python
# tests/unit/test_resource_store.py
def test_generate_resources_default_count():
    """Test that generate_resources creates 500 resources by default."""
    resources = generate_resources()
    assert len(resources) == 500

def test_tag_distribution_meets_requirements():
    """Test that each tag has at least 40 entries."""
    resources = generate_resources()
    tag_counts = {}
    for r in resources:
        tag_counts[r.search_tag] = tag_counts.get(r.search_tag, 0) + 1
    
    for tag, count in tag_counts.items():
        assert count >= 40, f"Tag {tag} has only {count} entries (need 40+)"

# tests/unit/test_dataset_validator.py (new file)
def test_validate_comprehensive_passes_for_valid_dataset():
    """Test that validation passes for properly generated dataset."""
    resources = generate_resources(500)
    report = validate_comprehensive(resources)
    assert report.overall_pass

def test_validate_comprehensive_fails_for_insufficient_count():
    """Test that validation fails when count is too low."""
    resources = generate_resources(400)
    report = validate_comprehensive(resources, expected_count=500)
    assert not report.total_count_pass
    assert not report.overall_pass

# tests/contract/test_list_responses.py
def test_list_resources_returns_500():
    """Test that /api/resources returns 500 resources."""
    response = client.get("/api/resources")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 500
    assert len(data["results"]) == 500
```

**Run Tests**:
```bash
pytest tests/unit/test_resource_store.py -v
pytest tests/unit/test_dataset_validator.py -v
pytest tests/contract/ -v
```

---

### Step 4: Update Documentation (15 min)

**Files to Update**:
- `README.md` - Update dataset size mention
- `CLAUDE.md` - Update any hardcoded 100-resource assumptions

**Example Updates**:

```markdown
# README.md
## Dataset

The resource store contains **500 deterministically generated resources** 
using Faker with seed=42. Each of the 12 tag categories has at least 40 entries.

Tags: home, car, technology, food, health, finance, travel, education, 
sports, music, fashion, nature
```

---

### Step 5: Validation & Quality Gates (30 min)

**Run all quality checks**:

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/

# Run all tests
pytest tests/ -v --cov=src --cov-report=term-missing

# Verify test coverage for new code
# Expected: dataset_validator.py should have >80% coverage
```

**Manual Validation**:

```bash
# Start the API
make start

# In another terminal, test endpoints
curl http://localhost:8000/api/resources | jq '.count'
# Should return 500

curl http://localhost:8000/api/tags | jq '.count'
# Should return 12

curl "http://localhost:8000/api/search?tag=automobile" | jq '.count'
# Should return resources (if Ollama running)
```

---

## Testing Checklist

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Ruff linting passes: `ruff check .`
- [ ] Type checking passes: `mypy src/`
- [ ] Code formatted: `ruff format --check .`
- [ ] Resource count is 500
- [ ] Each tag has ≥40 entries
- [ ] All UUIDs are unique
- [ ] Single tag per resource enforced
- [ ] Contextual content appropriate for tags
- [ ] API returns 500 resources at `/api/resources`
- [ ] Validation utilities work correctly
- [ ] Documentation updated

---

## Troubleshooting

### Issue: Tests fail with "expected 100, got 500"

**Solution**: Update test assertions to expect 500 resources.

```python
# Bad
assert len(resources) == 100

# Good
assert len(resources) == 500
```

### Issue: Tag has fewer than 40 entries

**Solution**: Check distribution algorithm. Ensure:
1. Only 12 tags selected (not 15)
2. Base allocation is 40 per tag
3. Remainder (20 resources) distributed

### Issue: UUIDs are not deterministic

**Solution**: Verify `random.seed(SEED)` called before UUID generation:

```python
random.seed(SEED)
Faker.seed(SEED)
# Then generate UUIDs
```

### Issue: Content not contextually appropriate

**Solution**: Check TAG_CONTENT_GENERATORS mapping. Ensure each tag has a generator function.

---

## Performance Notes

- **Generation time**: ~50ms for 500 resources (acceptable)
- **Memory usage**: ~150KB for 500 resources in memory
- **API response size**: ~150KB for `/api/resources` (increased from ~30KB)
- **LLM context size**: ~25KB for semantic search (was ~5KB)

---

## Next Steps

After implementation:
1. Run `/speckit.tasks` to generate task breakdown
2. Implement tasks iteratively with TDD
3. Commit with message: "feat: expand dataset to 500 resources with single-tag constraint"
4. Run integration tests with actual Ollama service
5. Measure performance baselines for 500-resource dataset

---

## Related Files

- **Spec**: [spec.md](spec.md)
- **Plan**: [plan.md](plan.md)
- **Research**: [research.md](research.md)
- **Data Model**: [data-model.md](data-model.md)
- **Contracts**: [contracts/openapi.yaml](contracts/openapi.yaml)
