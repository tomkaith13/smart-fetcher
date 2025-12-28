# Implementation Plan: Experimental ReACT Agent Endpoint

**Branch**: `[005-react-agent-endpoint]` | **Date**: December 28, 2025 | **Spec**: /Users/bt/personal/python/smart-fetcher/specs/005-react-agent-endpoint/spec.md
**Input**: Feature specification from /Users/bt/personal/python/smart-fetcher/specs/005-react-agent-endpoint/spec.md

**Note**: Filled by `/speckit.plan` workflow.

## Summary

Expose an experimental API endpoint that runs a single-turn ReACT-style agent which may call existing tools for NL search and resource validation, returning only the final answer. Citations are included only when explicitly requested. Log tool actions internally.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: FastAPI, Pydantic, DSPy, pytest, ruff, mypy; LLM provider: Ollama (`gpt-oss:20b`) by default, OpenAI-compatible as alternative  
**Storage**: N/A (in-memory session for single-turn)  
**Testing**: pytest (unit, integration, contract)  
**Target Platform**: Linux/macOS server (FastAPI app)  
**Project Type**: single backend service  
**Performance Goals**: 90% responses within 5s (SC-001)  
**Constraints**: Consistent JSON schema, zero ruff/mypy errors, comprehensive tests  
**Scale/Scope**: Single endpoint, single-turn agent, tools: NL search + resource validator

Decisions from Research:
- LLM/model: DSPy with local Ollama backend using `gpt-oss:20b` by default, pluggable to OpenAI-compatible providers.  
- Logging: Structured JSON-lines file logging for tool actions; in-memory summaries for audit in tests.

## Constitution Check

Pre-Phase 0 Gate (must pass to proceed):
- Testing Standards: Plan includes unit, integration, and contract tests for new endpoint → PASS (to be authored with implementation).  
- UX Consistency: Responses wrapped in consistent JSON with machine-readable error codes → PASS (defined in contracts).  
- Quality Gates: Commit to `pytest` passing, `ruff`/`mypy` zero errors → PASS (enforced in implementation).

Post-Phase 1 Re-check: Will verify contracts and data model alignment; any violations must be justified in Complexity Tracking.

### Post-Design Constitution Re-check (Phase 1)
- Contracts defined in `/specs/005-react-agent-endpoint/contracts/openapi.yaml` follow consistent JSON schemas → PASS.  
- Data model documented with validation rules and response shapes → PASS.  
- Testing plan exists (contract, integration, unit) and will be implemented with the feature → PASS.  
- No exceptions required at this stage.

## Project Structure

### Documentation (this feature)

```text
specs/005-react-agent-endpoint/
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
│   ├── routes.py            # Add experimental agent endpoint
│   └── schemas.py           # Add request/response models
├── services/
│   ├── nl_search_service.py # Existing tool
│   ├── resource_store.py    # Existing storage abstraction
│   ├── semantic_search.py   # Existing semantic search
│   └── agent/               # NEW: agent orchestration (if needed)
└── utils/
    ├── link_verifier.py     # Resource validation tool
    └── dataset_validator.py # Dataset validation

tests/
├── contract/                # NEW: test_agent_contract.py
├── integration/             # NEW: test_agent_api.py
└── unit/                    # NEW: test_agent_orchestrator.py (if orchestration added)
```

**Structure Decision**: Single backend service with FastAPI; add a new experimental route and a lightweight DSPy-based `services/agent/` orchestrator that invokes existing NL search and link verification tools via DSPy tools.

## Phase 2 Implementation Plan

- Add `src/services/agent/react_agent.py` implementing a DSPy ReACT-style agent:
    - Wrap existing tools as DSPy `Tool` functions: `nl_search(query)` and `validate_resource(url)`.
    - Compose an agent module that plans, calls tools, and produces a final answer without exposing tool traces.
- Add experimental route in `src/api/routes.py`: `POST /experimental/agent`.
- Update `src/api/schemas.py` with request/response models aligned to OpenAPI.
- Implement structured logging of tool actions to JSON lines.
- Tests:
    - Contract: schema compliance for success and error cases.
    - Integration: endpoint behavior, citations only on request.
    - Unit: agent orchestrator logic, tool wrapping and error handling.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None currently | N/A | N/A |
