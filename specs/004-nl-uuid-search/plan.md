# Implementation Plan: Natural Language UUID Search

**Branch**: `004-nl-uuid-search` | **Date**: 2025-12-27 | **Spec**: specs/004-nl-uuid-search/spec.md
**Input**: Feature specification from `specs/004-nl-uuid-search/spec.md`

**Note**: Generated and maintained by the `/speckit.plan` workflow.

## Summary

Enable natural language queries to discover resources by extracting domain tags via the existing inference stack (DSPy + Ollama), mapping tags to canonical resource UUIDs, and returning verified internal deep links of the form `/resources/{uuid}`. The DSPy extractor's reasoning is returned once at the top level of the response (not duplicated per item) to enhance transparency without redundancy. Preserve current API behavior, add NL query entrypoint, and enforce a default cap of 5 results with consistent JSON response wrapping.

## Technical Context

**Language/Version**: Python 3.13 (per pyproject requires-python >=3.13)  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, DSPy, httpx  
**Storage**: In-memory `ResourceStore` seeded with canonical resources (UUID/title/summary/tags)  
**Testing**: pytest, pytest-asyncio; structured `tests/contract`, `tests/integration`, `tests/unit`  
**Target Platform**: Linux/macOS server (FastAPI via Uvicorn)  
**Project Type**: Single backend project  
**Performance Goals**: NL query → response under 2s for 90% (SC-001)  
**Constraints**: Zero fabricated links; consistent JSON wrapping; ruff/mypy clean  
**Scale/Scope**: Small service; ~100 in-memory resources; extensible to larger datasets

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Code Quality: Type annotations present; functions <50 lines target; ruff/mypy required. Plan adheres and will enforce in new modules.
- Testing Standards: Unit/integration/contract tests required; external services mocked in unit. New NL endpoint will include contract + integration tests.
- UX Consistency: Responses wrapped (`results/count/query`); errors include `error/code/query` with correct HTTP statuses. FR-011 updated to mandate JSON-wrapped responses with client-side bulleted rendering (no raw bullet text from server). The `reasoning` field is included at the top-level of the response.

Gate Status (pre-Phase 0): PASS — No violations identified. Any exceptions will be documented in Complexity Tracking if they arise.

Gate Status (post-Phase 1): PASS — Design aligns with Code Quality, Testing Standards, and UX Consistency. New NL endpoint contracts and docs created; tests to be added during implementation.

## Project Structure

### Documentation (this feature)

```text
specs/004-nl-uuid-search/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── openapi.yaml
```

### Source Code (repository root)

```text
src/
├── api/
│   ├── routes.py
│   └── schemas.py
├── models/
│   └── resource.py
├── services/
│   ├── resource_store.py
│   └── semantic_search.py
└── main.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Single FastAPI backend with services for inference and resource store. NL search will integrate alongside existing `/search` and `/resources` endpoints, adding an NL entrypoint while reusing `SemanticSearchService` and `ResourceStore`.

## Complexity Tracking

No constitutional violations anticipated. Will update if constraints require exceptions.
