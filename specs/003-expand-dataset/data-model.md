# Phase 1: Data Model

**Feature**: Expand Dataset for Semantic Search Testing  
**Date**: 2025-12-26  
**Phase**: Design

## Entities

### Resource (Existing - No Changes)

**Description**: Searchable item with UUID, name, description, and single tag. Represents fundamental unit in semantic search system.

**Attributes**:
- `uuid: str` - Unique identifier (UUID v4 format)
- `name: str` - Human-readable resource title
- `description: str` - Detailed text content for semantic matching
- `search_tag: str` - Single categorical tag from predefined vocabulary

**Constraints**:
- UUID must be unique across all resources
- search_tag must be from TAG_CATEGORIES list
- Each resource has exactly one tag (no multi-tagging)

**Relationships**:
- None (flat structure, no foreign keys)

**Pydantic Model** (existing at `src/models/resource.py`):
```python
from pydantic import BaseModel, Field

class Resource(BaseModel):
    uuid: str = Field(..., description="Unique resource identifier")
    name: str = Field(..., description="Resource title")
    description: str = Field(..., description="Resource description")
    search_tag: str = Field(..., description="Single categorical tag")
```

---

### ValidationReport (New)

**Description**: Structured validation results for dataset integrity checks. Used by validation utilities to report pass/fail status for each requirement.

**Attributes**:
- `total_count_pass: bool` - Whether total count matches expected (500)
- `actual_count: int` - Actual number of resources
- `expected_count: int` - Expected number (500)
- `tag_distribution: dict[str, tuple[bool, int]]` - Per-tag validation: tag → (pass ≥40, actual count)
- `unique_uuids: bool` - Whether all UUIDs are unique
- `single_tags: bool` - Whether all resources have exactly one tag
- `schema_valid: bool` - Whether all resources match Resource model
- `overall_pass: bool` - Combined pass/fail status

**Constraints**:
- overall_pass is True only if all individual checks pass
- tag_distribution keys must match TAG_CATEGORIES

**Pydantic Model** (new at `src/utils/dataset_validator.py`):
```python
from pydantic import BaseModel, Field

class ValidationReport(BaseModel):
    total_count_pass: bool
    actual_count: int
    expected_count: int
    tag_distribution: dict[str, tuple[bool, int]]
    unique_uuids: bool
    single_tags: bool
    schema_valid: bool
    overall_pass: bool
    
    def summary(self) -> str:
        """Generate human-readable summary of validation results."""
        lines = [
            f"Total Count: {'✅' if self.total_count_pass else '❌'} ({self.actual_count}/{self.expected_count})",
            f"Unique UUIDs: {'✅' if self.unique_uuids else '❌'}",
            f"Single Tags: {'✅' if self.single_tags else '❌'}",
            f"Schema Valid: {'✅' if self.schema_valid else '❌'}",
            "\nTag Distribution:"
        ]
        for tag, (passed, count) in self.tag_distribution.items():
            status = '✅' if passed else '❌'
            lines.append(f"  {tag}: {status} ({count} resources)")
        lines.append(f"\nOverall: {'✅ PASS' if self.overall_pass else '❌ FAIL'}")
        return "\n".join(lines)
```

---

### TagContentGenerator (New - Internal)

**Description**: Function type for tag-specific content generation. Maps tag names to functions that generate contextually appropriate resource names and descriptions.

**Type Signature**:
```python
from typing import Callable, TypeAlias
from faker import Faker

TagContentGenerator: TypeAlias = Callable[[Faker], dict[str, str]]
# Returns: {"name": str, "description": str}
```

**Usage Pattern**:
```python
TAG_CONTENT_GENERATORS: dict[str, TagContentGenerator] = {
    "home": lambda fake: {
        "name": f"{fake.street_name()} {random.choice(['House', 'Residence', 'Property'])}",
        "description": f"Located at {fake.address()}. Features {fake.catch_phrase()}."
    },
    "car": lambda fake: {
        "name": f"{fake.color()} {random.choice(['Sedan', 'SUV', 'Coupe', 'Truck'])}",
        "description": f"{fake.company()} vehicle with {fake.bs()} technology."
    },
    # ... 10 more tag-specific generators
}
```

**Constraints**:
- Must use only Faker methods (no external APIs)
- Output must be deterministic with seeded Faker
- Name should be 3-8 words, description 1-3 sentences

---

## Data Flows

### Dataset Generation Flow

```
1. Call generate_resources(count=500, seed=SEED)
   ↓
2. Initialize random.seed(SEED) and Faker.seed(SEED)
   ↓
3. Calculate tag distribution:
   - Select 12 tags from TAG_CATEGORIES (most common in original 100)
   - Assign base_count = 40 to each tag (480 total)
   - Calculate remainder = 500 - 480 = 20
   - Distribute remainder proportionally
   ↓
4. For each tag in distribution:
   For count in tag's allocation:
     a. Get tag-specific content generator
     b. Generate UUID with seeded random
     c. Generate name + description using generator
     d. Create Resource(uuid, name, description, tag)
     e. Append to resources list
   ↓
5. Return list[Resource] (500 items)
```

### Validation Flow

```
1. Call validate_comprehensive(resources)
   ↓
2. Run individual validators:
   - validate_total_count(resources, expected=500)
   - validate_tag_distribution(resources, min_per_tag=40)
   - validate_unique_uuids(resources)
   - validate_single_tags(resources)
   - validate_schemas(resources)
   ↓
3. Aggregate results into ValidationReport
   ↓
4. Set overall_pass = all checks passed
   ↓
5. Return ValidationReport
```

### ResourceStore Initialization Flow

```
1. Create ResourceStore(resources=None)
   ↓
2. If resources is None:
     resources = generate_resources(count=500)  # Changed from 100
   ↓
3. Build indices:
   For each resource:
     - Add to _resources[uuid]
     - Add uuid to _tags_to_uuids[tag]
   ↓
4. Compute _unique_tags list
   ↓
5. Store ready for queries
```

---

## State Transitions

**Resource Lifecycle**: Immutable after creation (no state transitions)

**ValidationReport Lifecycle**: Created once per validation run (no mutations)

**ResourceStore State**:
1. **Empty** → (initialize with None) → **Populated** (500 resources)
2. **Empty** → (initialize with list) → **Populated** (custom count)

No state transitions after initialization (read-only store).

---

## Schema Changes

### Modified: `src/services/resource_store.py`

**Change**: Update default count in `generate_resources()`

```python
# BEFORE
def generate_resources(count: int = 100) -> list[Resource]:
    """Generate deterministic resources using Faker with a fixed seed."""

# AFTER  
def generate_resources(count: int = 500, seed: int = SEED) -> list[Resource]:
    """Generate deterministic resources using Faker with a fixed seed.
    
    Args:
        count: Number of resources to generate (default 500).
        seed: Random seed for reproducibility (default SEED constant).
    
    Returns:
        List of Resource objects with contextually appropriate content per tag.
    """
```

**Breaking Change**: Yes - default count changes from 100 to 500. Existing code relying on implicit 100 count must be updated.

**Migration**: 
- Tests asserting specific counts: Update expected values
- Code expecting 100 resources: Pass explicit `count=100` parameter
- UUIDs will change: Regenerate any stored/expected UUID references

### New: `src/utils/dataset_validator.py`

**Purpose**: Validation utilities for dataset integrity

**Exports**:
- `ValidationReport` (Pydantic model)
- `validate_comprehensive(resources: list[Resource]) -> ValidationReport`
- `validate_total_count(resources, expected) -> bool`
- `validate_tag_distribution(resources, min_per_tag) -> dict[str, int]`
- `validate_unique_uuids(resources) -> bool`
- `validate_single_tags(resources) -> bool`
- `validate_schemas(resources) -> bool`

---

## Dependencies Between Entities

```
ValidationReport
  ↓ (validates)
Resource
  ↓ (generated by)
TagContentGenerator
  ↓ (uses)
Faker (external)

ResourceStore
  ↓ (contains)
Resource
  ↓ (validated by)
ValidationReport
```

**No circular dependencies** - clean unidirectional flow.

---

## Indexing Strategy

**Existing Indices** (maintained):
- `_resources: dict[str, Resource]` - O(1) lookup by UUID
- `_tags_to_uuids: dict[str, set[str]]` - O(1) lookup by tag

**No new indices required** - existing structure supports 500 resources efficiently.

**Performance Impact**:
- Memory: 100 resources × 300 bytes ≈ 30KB → 500 resources × 300 bytes ≈ 150KB (acceptable)
- Lookup time: O(1) for both 100 and 500 (hash tables)
- Iteration time: O(n) scales linearly (100ms → 500ms for full iteration)

---

## Next Steps

Proceed to:
1. Generate contracts (OpenAPI schema updates if API exposes count)
2. Create quickstart.md with examples
3. Update agent context with new decisions
