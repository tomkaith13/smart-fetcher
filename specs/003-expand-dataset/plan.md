# Implementation Plan: Expand Dataset for Semantic Search Testing

**Branch**: `003-expand-dataset` | **Date**: 2025-12-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-expand-dataset/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Expand the existing test dataset from 100 to 500 resources with strict single-tag categorization, ensuring each tag has at least 40 entries with proportional distribution of remainder. Generate synthetic data programmatically using existing Faker library with contextually appropriate content (e.g., "home" tags get house-related content with natural variation). Maintain deterministic generation for reproducibility. Add validation utilities to verify tag distribution, resource counts, and schema compliance.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Faker (existing), Pydantic (existing), pytest (existing)  
**Storage**: In-memory (ResourceStore class, no persistence required)  
**Testing**: pytest with unit tests for generation logic and validation functions  
**Target Platform**: Local development, CI environments (Linux/macOS)
**Project Type**: Single project (data generation utility within existing service)  
**Performance Goals**: Generate 500 resources in <1 second (on MacBook Pro M1 2020 or GitHub Actions ubuntu-latest runner), deterministic output with fixed seed  
**Constraints**: No new external dependencies, maintain backward compatibility with existing ResourceStore API, single-tag per resource constraint  
**Scale/Scope**: 500 total resources, 12 of 15 existing tag categories used (home, car, technology, food, health, finance, travel, education, sports, music, fashion, nature; excluding work, family, art due to 40-per-tag constraint), minimum 40 resources per tag

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Code Quality** | ✅ PASS | All new code will use Pydantic models (existing), type hints, ruff formatting/linting. Data generation logic will be decomposed into single-responsibility functions (<50 lines). Comprehensive docstrings for all public functions. Tag-specific generators use lambda functions for clarity. |
| **II. Testing Standards** | ✅ PASS | Unit tests in `tests/unit/test_dataset_validator.py` for generation logic and validation. Contract tests updated in `tests/contract/test_list_responses.py` and `test_resource_responses.py`. No external services (Faker is deterministic with seed). Integration tests benefit from larger dataset without changes. |
| **III. UX Consistency** | ✅ PASS | No API changes - existing ResourceStore interface maintained. Validation functions return structured ValidationReport Pydantic model. No CLI changes needed. All responses remain wrapped in descriptive objects ({"results": [...], "count": N}). |
| **Development Workflow** | ✅ PASS | All quality gates pass: pytest (new tests for expansion logic), ruff check/format (zero errors), mypy (type safety verified with Pydantic). No CI changes needed - existing workflow sufficient. |

**Post-Phase 1 Re-evaluation**: ✅ All principles maintained. Research revealed tag count adjustment (15→12) necessary to meet 40-per-tag requirement with 500 total. No constitution violations. Data model uses existing patterns. Validation utilities follow structured return pattern.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── resource.py           # [EXISTING] Pydantic Resource model
├── services/
│   ├── resource_store.py     # [MODIFY] Update generate_resources() to support 500 count
│   └── semantic_search.py    # [NO CHANGE] Uses ResourceStore, unaffected
└── utils/                    # [NEW] Data generation utilities
    └── dataset_validator.py  # [NEW] Validation functions for tag distribution

tests/
├── contract/
│   └── test_resource_responses.py  # [MODIFY] Update fixtures to use 500 resources
├── integration/
│   └── test_search_api.py          # [NO CHANGE] May benefit from larger dataset
└── unit/
    ├── test_resource_store.py      # [MODIFY] Update count assertions
    └── test_dataset_validator.py   # [NEW] Test validation logic
```

**Structure Decision**: Single project structure maintained. All changes confined to existing `src/services/resource_store.py` module (update generation function) and new `src/utils/dataset_validator.py` utility module for validation logic. No architectural changes required - pure data layer enhancement.

**Post-Implementation Optimization**: During implementation, the semantic search was optimized to handle the 5x dataset increase efficiently. The service was refactored from a UUID-selection approach (sending 500 resources to LLM) to a tag-classification approach (sending 12 unique tags to LLM). This optimization achieved:
- 97% reduction in LLM context size (500 resources → 12 tags)
- Simpler classification task for improved reliability
- O(1) resource lookup via pre-built tag index
- Faster inference with smaller input/output
- Predictable results (all resources for matched category)

This change required:
- New `ResourceStore.get_by_tag()` method for efficient tag-based lookup
- Dynamic `SemanticResourceFinder` signature creation with tags in descriptions
- Two-step search process: classify tag → lookup resources
- Test updates to mock `best_matching_tag` instead of `matching_uuids`

See [research.md](research.md#6-semantic-search-optimization-post-implementation) for detailed analysis and implementation.

## Complexity Tracking

> **No constitution violations - this section left empty per template guidance**

This feature introduces no complexity requiring justification. All changes use existing dependencies (Faker, Pydantic), maintain existing architecture (in-memory ResourceStore), and follow established patterns (deterministic generation with seeds).
