# Implementation Plan: Smart Tag-Based Resource Fetcher

**Branch**: `001-dspy-tag-fetcher` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-dspy-tag-fetcher/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a FastAPI application that uses DSPy with Ollama (gpt-oss:20b) to perform semantic tag-based search across 100 in-memory resources. The system accepts search tags via REST API, uses LLM inference to find semantically related resources (synonym matching), and returns results in a wrapped JSON format.

## Technical Context

**Language/Version**: Python 3.13 (specified in .python-version)
**Primary Dependencies**: FastAPI, DSPy, Ollama (gpt-oss:20b), uvicorn, pydantic
**Storage**: In-memory (list/dict of Resource objects, deterministic seed)
**Testing**: pytest (with coverage ≥80% per constitution)
**Target Platform**: Local development server (macOS/Linux)
**Project Type**: Single API application
**Performance Goals**: <3s for tag search, <500ms for UUID lookup (per SC-001, SC-004)
**Constraints**: Single-instance mode, no auth required, 100 resources max
**Scale/Scope**: Demo/prototype scope, 100 pre-generated resources, 3 API endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Gate Evaluation

| Principle | Requirement | Plan Compliance | Status |
|-----------|-------------|-----------------|--------|
| I. Code Quality | Type annotations, ruff, docstrings, <50 line functions | Will use Pydantic models (typed), ruff for linting/formatting | ✅ PASS |
| II. Testing Standards | 80% coverage, unit/integration/contract dirs, mocked externals | pytest with coverage, mock Ollama in unit tests | ✅ PASS |
| III. UX Consistency | Actionable errors, consistent JSON output, exit codes | Wrapped JSON responses, structured error format defined | ✅ PASS |
| IV. Performance | <30s timeout, bounded memory, async I/O, resource cleanup | <3s search target, 100 fixed resources, FastAPI async | ✅ PASS |

### Quality Gates Verification Plan

| Gate | Verification Command | Target |
|------|---------------------|--------|
| Tests | `uv run pytest` | All pass |
| Coverage | `uv run pytest --cov` | ≥80% |
| Linting | `uv run ruff check .` | 0 errors |
| Type Check | `uv run mypy src/` | 0 errors |
| Format | `uv run ruff format --check .` | 0 errors |

**Gate Status**: ✅ All gates passed. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-dspy-tag-fetcher/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── openapi.yaml     # REST API contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # FastAPI app entry point
├── models/
│   ├── __init__.py
│   └── resource.py      # Resource Pydantic model
├── services/
│   ├── __init__.py
│   ├── resource_store.py    # In-memory resource storage
│   └── semantic_search.py   # DSPy SemanticResourceFinder service (tag → matching resources)
└── api/
    ├── __init__.py
    ├── routes.py        # API endpoint definitions
    └── schemas.py       # Request/Response schemas

tests/
├── __init__.py
├── conftest.py          # Shared fixtures (mock Ollama, sample resources)
├── unit/
│   ├── __init__.py
│   ├── test_resource_store.py
│   └── test_semantic_search.py
├── integration/
│   ├── __init__.py
│   └── test_api_endpoints.py
└── contract/
    ├── __init__.py
    └── test_response_formats.py
```

**Structure Decision**: Single API application structure selected. This is a backend-only REST API with no frontend component. The `src/` directory contains the application code organized by layer (models, services, api), and `tests/` follows the constitution-mandated structure with unit, integration, and contract subdirectories.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations identified. Design follows minimal complexity principles.*

## Post-Phase 1 Constitution Re-Check

| Principle | Design Artifact | Compliance Status |
|-----------|----------------|-------------------|
| I. Code Quality | data-model.md defines typed Pydantic models | ✅ PASS |
| II. Testing Standards | Project structure includes unit/integration/contract test dirs | ✅ PASS |
| III. UX Consistency | OpenAPI contract defines consistent wrapped JSON responses | ✅ PASS |
| IV. Performance | Async endpoints, bounded 100 resources, in-memory storage | ✅ PASS |

**Post-Design Gate Status**: ✅ All gates passed. Ready for `/speckit.tasks`.

## Generated Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Research | [research.md](./research.md) | DSPy+Ollama integration, data generation patterns |
| Data Model | [data-model.md](./data-model.md) | Entity definitions, Pydantic schemas, relationships |
| API Contract | [contracts/openapi.yaml](./contracts/openapi.yaml) | OpenAPI 3.1 specification |
| Quickstart | [quickstart.md](./quickstart.md) | Setup and running instructions |
