# Implementation Plan: Rename Citations to Resources in Agent Endpoint

**Branch**: `006-rename-citations-resources` | **Date**: 2026-01-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-rename-citations-resources/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Rename the "citations" field to "resources" in the experimental/agent endpoint response to align terminology with the rest of the API. This is a refactoring task affecting response schemas, API documentation, test assertions, and internal code references. No behavioral changes - only field naming is updated.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: FastAPI 0.115.0+, Pydantic 2.10.0+  
**Storage**: N/A (API response schema change only)  
**Testing**: pytest 8.3.0+ (unit, integration, contract tests)  
**Target Platform**: Linux server (FastAPI REST API)  
**Project Type**: Single project (backend API)  
**Performance Goals**: No impact (field name change only)  
**Constraints**: No backward compatibility layer needed (experimental endpoint)  
**Scale/Scope**: Small refactoring - affects 1 endpoint, ~10 files (schemas, routes, tests, docs)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Code Quality** | ✅ PASS | Field rename maintains type safety. All Pydantic models and type hints will be updated. No function length or complexity impact. Docstrings will be updated to use "resources" terminology. |
| **II. Testing Standards** | ✅ PASS | All existing tests (unit, integration, contract) will be updated to validate "resources" field. Test names remain accurate (focus on behavior, not field names). No new feature, so new test types not required - updating existing assertions sufficient. |
| **III. UX Consistency** | ✅ PASS | Change improves API consistency by aligning agent endpoint terminology with other endpoints that already use "resources". Response structure unchanged - only field name updates. Error messages unaffected. |
| **Quality Gates** | ✅ PASS | All gates expected to pass: pytest (updated assertions), ruff (formatting maintained), mypy (type hints updated), ruff format (no style changes). |

## Project Structure

### Documentation (this feature)

```text
specs/006-rename-citations-resources/
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
│   └── resource.py              # Contains Resource/Citation data models
├── services/
│   └── agent/
│       └── react_agent.py       # Agent implementation using "citations" variable names
├── api/
│   ├── routes.py                # Agent endpoint handler
│   └── schemas.py               # AgentAnswerWithCitations Pydantic model
└── utils/

tests/
├── contract/
│   └── test_agent_contract.py   # Tests for AgentAnswerWithCitations schema
├── integration/
│   └── test_agent_api.py        # Integration tests checking "citations" field
└── unit/

README.md                         # API documentation with "citations" examples
specs/005-react-agent-endpoint/
└── contracts/
    └── openapi.yaml              # OpenAPI spec with "citations" field definition
```

**Structure Decision**: Single project structure. All changes are within the existing `src/` and `tests/` directories. The agent endpoint code is located in `src/api/` (routes, schemas) and `src/services/agent/` (implementation). Tests are organized by type (unit/integration/contract) as per constitution standards.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitutional principles are satisfied.
