# Data Model: Rename Citations to Resources

**Feature**: Rename Citations to Resources in Agent Endpoint  
**Date**: 2026-01-01

## Overview

This document describes the data model changes for renaming "citations" to "resources" in the agent endpoint. This is a refactoring task - no new entities are created, only existing entities are renamed.

## Entity Changes

### ResourceCitation (formerly Citation)

**Purpose**: Represents a reference/citation to a resource that was used by the agent to generate its answer.

**Attributes**:
- `title` (string): Human-readable title of the cited resource
- `url` (string): URL/path to access the cited resource (typically `/resources/{uuid}`)
- `summary` (string): Brief description of the resource content

**Validation Rules**:
- All fields are required (no optional fields)
- `url` must be a valid string (validation inherited from Pydantic)
- `title` and `summary` are free-form text

**Relationships**:
- Referenced by `AgentAnswerWithResources.resources` (list relationship)
- Represents a citation to a `Resource` entity (from `src/models/resource.py`), but does not directly reference it (decoupled)

**State Transitions**: None (immutable - created when agent generates response)

**Change Summary**: 
- Renamed from `Citation` to `ResourceCitation` for clarity
- No attribute changes
- No validation rule changes

---

### AgentAnswerWithResources (formerly AgentAnswerWithCitations)

**Purpose**: Response schema for agent endpoint when `include_sources=true` is specified.

**Attributes**:
- `answer` (string, inherited): The agent's generated answer
- `query` (string, inherited): The original user query
- `meta` (dict, inherited): Metadata about the response (e.g., `{"experimental": true}`)
- `resources` (list[ResourceCitation]): List of resource citations used by the agent (formerly `citations`)

**Validation Rules**:
- Inherits validation from `AgentAnswer` base class
- `resources` defaults to empty list if not provided
- `resources` can be empty (valid when no sources found or include_sources=false)

**Relationships**:
- Extends `AgentAnswer` (inheritance)
- Contains list of `ResourceCitation` (composition)

**State Transitions**: None (response object - created once and returned)

**Change Summary**:
- Renamed from `AgentAnswerWithCitations` to `AgentAnswerWithResources`
- Renamed field `citations` to `resources`
- No other attribute or validation changes

---

## No New Entities

This feature does not introduce new entities. It only renames existing entities for consistency with the rest of the API.

---

## Entity Relationship Diagram

```
AgentAnswer (base class)
    ├── answer: string
    ├── query: string
    └── meta: dict

AgentAnswerWithResources (extends AgentAnswer)
    └── resources: list[ResourceCitation]
            └── ResourceCitation
                ├── title: string
                ├── url: string
                └── summary: string
```

---

## Mapping to Functional Requirements

| Requirement | Entity/Attribute | Notes |
|-------------|------------------|-------|
| FR-001 | `AgentAnswerWithResources.resources` | Field renamed from "citations" |
| FR-002 | `ResourceCitation` attributes | Structure unchanged - only class name updated |
| FR-003 | `AgentAnswerWithResources` schema | OpenAPI definition will reflect new name |
| FR-007 | `ResourceCitation`, `AgentAnswerWithResources` | Class names updated for consistency |

---

## Implementation Notes

**No database changes**: This is purely an API response schema change. No persistence layer affected.

**No migration needed**: Experimental endpoint with no published API contract. Direct cutover is appropriate.

**Type safety preserved**: All Pydantic type hints remain intact. TypeScript/mypy will catch any missed references during refactoring.
