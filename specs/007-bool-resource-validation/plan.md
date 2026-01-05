# Implementation Plan: Boolean Resource Validation with Hallucination Filtering

**Branch**: `007-bool-resource-validation` | **Date**: 2026-01-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-bool-resource-validation/spec.md`

**User Constraint**: Ensure we only change the experimental endpoint and nothing else. All other functionality should be untouched. All tests should pass.

## Summary

Modify the `_validate_resource_tool` function in the ReACT agent to return a boolean instead of a string, implement filtering logic in the experimental agent endpoint to exclude invalid resources, add comprehensive logging for hallucination detection, and return HTTP 404 when all resources fail validation. This change isolates to the `/experimental/agent` endpoint only, leaving all other endpoints and functionality untouched.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: FastAPI 0.115+, DSPy 2.5+, Pydantic 2.10+
**Storage**: In-memory (deterministic seed-based resource generation)
**Testing**: pytest with unit/integration/contract structure
**Target Platform**: Linux/macOS server (uvicorn)
**Project Type**: Single web API project
**Performance Goals**: <10% increase in endpoint response time
**Constraints**: Maintain backward compatibility with response structure, logging must not block processing
**Scale/Scope**: Single endpoint modification, ~200 LOC changes across 2-3 files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Code Quality** | ✅ PASS | Type annotations required (bool return, Pydantic models). Functions <50 lines. Ruff linting mandatory. Docstrings for modified functions. |
| **II. Testing Standards** | ✅ PASS | New tests required: unit tests for bool validation logic, integration tests for filtering behavior, contract tests for 404 response. All tests must pass. |
| **III. UX Consistency** | ✅ PASS | Consistent JSON error responses (404 with error/code/query). Maintains existing response structure for success cases. |
| **Quality Gates** | ✅ PASS | All gates enforced: pytest passing, ruff check, mypy, ruff format. No gate bypasses needed. |

**Gate Status**: ✅ APPROVED - No violations, all principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/007-bool-resource-validation/
├── plan.md              # This file
├── research.md          # Phase 0: Design decisions
├── data-model.md        # Phase 1: Data structures
├── quickstart.md        # Phase 1: Testing guide
├── contracts/           # Phase 1: API contracts
│   └── agent-404.json   # HTTP 404 error response contract
└── tasks.md             # Phase 2: NOT created by this command
```

### Source Code (repository root)

```text
src/
├── models/              # Pydantic models (unchanged)
├── services/
│   └── agent/
│       └── react_agent.py          # MODIFIED: Change _validate_resource_tool return type
├── api/
│   ├── routes.py                    # MODIFIED: Add filtering logic in /experimental/agent
│   └── schemas.py                   # POTENTIALLY MODIFIED: Add 404 error schema if needed
└── utils/
    └── agent_logger.py              # POTENTIALLY MODIFIED: Add hallucination logging helpers

tests/
├── contract/
│   └── test_agent_contract.py       # MODIFIED: Add 404 contract test
├── integration/
│   └── test_agent_api.py            # MODIFIED: Add filtering and 404 integration tests
└── unit/
    └── test_agent_orchestrator.py   # MODIFIED: Add boolean validation unit tests
```

**Structure Decision**: Single project structure (already established). Changes isolated to:
1. `src/services/agent/react_agent.py`: Modify `_validate_resource_tool` to return `bool` instead of `str`
2. `src/api/routes.py`: Add filtering logic in `run_experimental_agent` endpoint
3. Test files: Add comprehensive tests covering all new behaviors

## Complexity Tracking

**No violations** - all constitution principles satisfied without exceptions.

## Phase 0: Research & Decisions

### Research Tasks

1. **Decision: Validation Function Return Type**
   - **Question**: How to change `_validate_resource_tool` from returning string to boolean without breaking DSPy tool contract?
   - **Research**: Investigate DSPy tool requirements, ensure boolean return is compatible with ReAct agent expectations

2. **Decision: Logging Strategy**
   - **Question**: What logging approach ensures hallucination detection without blocking request processing?
   - **Research**: Review existing `agent_logger` utilities, determine best practices for WARNING vs ERROR level logging with try/except

3. **Decision: Response Structure for Empty Results**
   - **Question**: How to structure HTTP 404 error response to maintain consistency with existing error patterns?
   - **Research**: Review existing `ErrorResponse` schema, ensure "no valid resources found" message aligns with UX consistency principle

4. **Decision: Filtering Implementation Location**
   - **Question**: Where should resource filtering logic reside - in ReACT agent or endpoint handler?
   - **Research**: Evaluate separation of concerns, determine if filtering belongs in agent.run() or routes.py

### Key Decisions

#### Research Output Location
See `research.md` for detailed findings and rationale for each decision above.

## Phase 1: Design & Contracts

### Data Model Changes

**Location**: `data-model.md`

Key changes:
- `_validate_resource_tool`: Return type changes from `str` to `bool`
- Resource filtering logic: List comprehension to filter resources where `is_valid == True`
- Error response model: Potential addition of 404-specific error schema

### API Contracts

**Location**: `contracts/agent-404.json`

New contract for all-resources-fail scenario:
```json
{
  "error": "no valid resources found",
  "code": "NO_VALID_RESOURCES",
  "query": "<original query>"
}
```

HTTP Status: 404
Trigger Condition: When `include_sources=true` and all resources fail validation

### Quickstart Guide

**Location**: `quickstart.md`

Testing guide covering:
1. How to test boolean validation function
2. How to trigger hallucination scenarios
3. How to verify logging output
4. How to test 404 response

## Phase 2: Implementation Tasks

**NOTE**: Task breakdown is generated by `/speckit.tasks` command, not by `/speckit.plan`.

The following are high-level implementation areas (detailed tasks in `tasks.md`):

### Area 1: Validation Function Modification
- Modify `_validate_resource_tool` in `react_agent.py`
- Change return type from `str` to `bool`
- Update docstring and type hints
- Ensure DSPy tool compatibility

### Area 2: Filtering Logic Implementation
- Add resource filtering in `run_experimental_agent` (routes.py)
- Implement list comprehension to exclude `is_valid == False`
- Add HTTP 404 response for all-fail scenario
- Preserve resource order per FR-007

### Area 3: Logging Implementation
- Add WARNING-level logging for hallucinations (FR-003)
- Add ERROR-level logging for validation exceptions (FR-006)
- Implement try/except to suppress logging failures (FR-009)
- Include resource details and validation failure reason (FR-004)

### Area 4: Testing
- Unit tests: Boolean return type, filtering logic, edge cases
- Integration tests: End-to-end filtering, 404 response, logging verification
- Contract tests: 404 error response schema validation
- Ensure all existing tests still pass (no regression)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| DSPy tool expects string return | HIGH | Research DSPy tool contract in Phase 0, validate with minimal test case |
| Filtering breaks existing agent behavior | HIGH | Only modify experimental endpoint, add comprehensive regression tests |
| Logging failures block requests | MEDIUM | Implement FR-009 suppression, test logging failure scenarios |
| Performance degradation >10% | MEDIUM | Benchmark before/after, optimize filtering if needed |

## Success Criteria Validation

Mapping spec success criteria to implementation verification:

- **SC-001** (100% hallucination filtering): Verified by integration tests with mock invalid resources
- **SC-002** (100% valid resource inclusion): Verified by integration tests confirming valid resources not excluded
- **SC-003** (All hallucinations logged): Verified by log capture in integration tests
- **SC-004** (<10% performance impact): Verified by before/after benchmarking (optional, not required for merge)
- **SC-005** (Maintain throughput): Verified by load testing (optional, not required for merge)

## Next Steps

After `/speckit.plan` completion:

1. ✅ Review `research.md` - ensure all design decisions documented
2. ✅ Review `data-model.md` - validate data structure changes
3. ✅ Review `contracts/` - confirm API contract accuracy
4. ✅ Review `quickstart.md` - verify testing approach
5. ⏭️ Run `/speckit.tasks` - generate detailed implementation tasks
6. ⏭️ Implement tasks following constitution gates
7. ⏭️ Verify all tests pass before merge
