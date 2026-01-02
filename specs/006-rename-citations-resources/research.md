# Research: Rename Citations to Resources

**Feature**: Rename Citations to Resources in Agent Endpoint  
**Date**: 2026-01-01  
**Status**: Complete

## Overview

This document consolidates findings from Phase 0 research to resolve all technical unknowns identified in the Technical Context section of [plan.md](plan.md).

## Research Tasks

### Task 1: Identify all files containing "citations" references

**Objective**: Locate every file that references "citations" or "Citation" to ensure complete renaming coverage.

**Decision**: Complete file inventory identified

**Findings**:
- **Source files** (7 occurrences across 2 files):
  - `src/api/schemas.py`: Citation class, AgentAnswerWithCitations class, field descriptions
  - `src/services/agent/react_agent.py`: Import statement, variable names, field assignment, comments
  - `src/api/routes.py`: Documentation string

- **Test files** (30+ occurrences across 3 files):
  - `tests/contract/test_agent_contract.py`: Test function names, test assertions
  - `tests/integration/test_agent_api.py`: Test function names, field access, comments
  - `tests/unit/test_agent_orchestrator.py`: Test function names, field access, comments

- **Documentation files**:
  - `README.md`: API example showing "citations" field
  - `specs/005-react-agent-endpoint/contracts/openapi.yaml`: OpenAPI schema definition

**Rationale**: Comprehensive search ensures no references are missed. All occurrences must be updated to maintain consistency and prevent confusion.

---

### Task 2: Determine naming conventions for renamed entities

**Objective**: Establish consistent naming patterns for the refactored code.

**Decision**: Use "Resource" terminology consistently

**Naming Mappings**:
| Current Name | New Name | Rationale |
|--------------|----------|-----------|
| `Citation` (class) | `ResourceCitation` | More descriptive - indicates it's a citation/reference to a resource |
| `AgentAnswerWithCitations` | `AgentAnswerWithResources` | Direct field name correspondence |
| `citations` (field) | `resources` | Aligns with rest of API (e.g., `/resources/{uuid}` endpoint) |
| `citations` (variable) | `resources` | Consistent with field name |
| `include_sources` (parameter) | No change | Parameter name is semantic - describes what to include, not what it's called |

**Rationale**: 
- "ResourceCitation" is more explicit than just "Resource" (which is already used for the Resource model in `src/models/resource.py`)
- Maintains clarity about the distinction between a Resource (the full data model) and a ResourceCitation (the reference/citation to that resource)
- Preserves the `include_sources` parameter name because it describes the user intent ("include sources"), not the internal field name

---

### Task 3: Validate no breaking changes to response structure

**Objective**: Confirm that only the field name changes, not the data structure or content.

**Decision**: Structure remains identical

**Validation**:
- Field type: `list[ResourceCitation]` (same structure as `list[Citation]`)
- Field contents: `{"title": str, "url": str, "summary": str}` (unchanged)
- Optional field: Present only when `include_sources=true` (unchanged behavior)
- Empty array vs omitted: Controlled by `include_sources` flag (unchanged logic)

**Rationale**: This is a pure refactoring - zero functional changes. All tests should pass after updating field name assertions.

---

### Task 4: Review Pydantic model inheritance patterns

**Objective**: Understand how `AgentAnswerWithCitations` extends `AgentAnswer` to ensure proper refactoring.

**Decision**: Standard Pydantic inheritance - simple field addition

**Findings**:
```python
class AgentAnswer(BaseModel):
    answer: str
    query: str
    meta: dict

class AgentAnswerWithCitations(AgentAnswer):  # Inherits all fields from AgentAnswer
    citations: list[Citation] = Field(default_factory=list)
```

After refactoring:
```python
class AgentAnswerWithResources(AgentAnswer):  # Same inheritance pattern
    resources: list[ResourceCitation] = Field(default_factory=list)
```

**Rationale**: Straightforward inheritance - no complex patterns to preserve. Renaming class and field is safe.

---

## Alternatives Considered

### Alternative 1: Keep "Citation" class name, only rename field
**Rejected because**: Inconsistent - having a "Citation" class but "resources" field creates confusion. Full rename maintains clarity.

### Alternative 2: Use "Resource" instead of "ResourceCitation"
**Rejected because**: "Resource" is already the name of the main data model in `src/models/resource.py`. Using "ResourceCitation" makes the distinction clear - this is a citation/reference to a resource, not the full resource object.

### Alternative 3: Add backward compatibility alias
**Rejected because**: This is an experimental endpoint (clearly marked in documentation). No production consumers exist. Adding compatibility code adds complexity with no benefit.

---

## Impact Analysis

**Code Changes**: 
- 2 source files (schemas, agent service)
- 3 test files (contract, integration, unit)
- 2 documentation files (README, OpenAPI spec)
- ~35 total occurrences of "citation(s)" to update

**Risk Level**: **Low**
- Experimental endpoint (clearly documented)
- No external consumers (internal API)
- All changes are textual (field names, variable names)
- No logic changes
- All tests will be updated simultaneously

**Migration Path**: Not needed (experimental endpoint, no published API)

---

## Summary

All technical unknowns resolved. The refactoring is straightforward:
1. Rename `Citation` class to `ResourceCitation`
2. Rename `AgentAnswerWithCitations` to `AgentAnswerWithResources`
3. Rename `citations` field to `resources` 
4. Update all variable names, comments, and documentation
5. Update all test assertions

No NEEDS CLARIFICATION markers remain. Ready for Phase 1 design.
