# Research: Boolean Resource Validation Design Decisions

**Feature**: 007-bool-resource-validation
**Date**: 2026-01-04

## Overview

This document captures research findings and design decisions for implementing boolean resource validation with hallucination filtering in the experimental agent endpoint.

## Research Questions & Findings

### 1. Validation Function Return Type

**Question**: How to change `_validate_resource_tool` from returning string to boolean without breaking DSPy tool contract?

**Research Findings**:

Based on codebase analysis and DSPy patterns:

- **Current Implementation**: The `_validate_resource_tool` returns a descriptive string like "Resource {url} is valid" or "Resource {url} is invalid or unreachable"
- **DSPy Tool Contract**: DSPy tools are typically designed to return strings that become part of the agent's reasoning trajectory
- **String Conversion**: DSPy's ReAct module converts non-string return values to strings automatically using `str(return_value)`

**Decision**: **Change return type to `bool`**

**Rationale**:
1. **Automatic String Conversion**: DSPy will convert `True` → `"True"` and `False` → `"False"` automatically when building the agent's trajectory
2. **Type Safety**: Boolean return provides stronger type guarantees and clearer semantics
3. **Separation of Concerns**: The tool should return the validation result; the agent/endpoint handles interpretation
4. **Testability**: Boolean returns are easier to test and mock than string parsing

**Implementation**:
```python
def _validate_resource_tool(self, url: str) -> bool:
    """Tool function for resource validation (called by DSPy ReAct).

    Returns:
        bool: True if valid, False if invalid/hallucinated.
    """
    try:
        is_valid = self.link_verifier.verify_link(url)
        if not is_valid:
            # Log hallucination at WARNING level (FR-003)
            self._log_hallucination(url)
        return is_valid
    except Exception as e:
        # FR-006: Exception → treat as invalid, log at ERROR
        self._log_validation_error(url, e)
        return False
```

**Alternatives Considered**:
- **Keep string return**: Rejected - doesn't solve the filtering problem, requires string parsing
- **Return dict with metadata**: Rejected - overly complex, DSPy would stringify it anyway
- **Return custom enum**: Rejected - overkill for binary valid/invalid state

---

### 2. Logging Strategy

**Question**: What logging approach ensures hallucination detection without blocking request processing?

**Research Findings**:

Current logging infrastructure:
- `src/utils/agent_logger.py`: Provides structured logging for agent events
- Existing methods: `log_session_start`, `log_session_end`, `log_tool_action`
- No specific hallucination logging methods

**Decision**: **Use Python's standard logging with WARNING/ERROR levels, wrapped in try/except**

**Rationale**:
1. **Non-Blocking**: Wrapping logger calls in try/except prevents logging failures from blocking requests (FR-009)
2. **Standard Levels**: WARNING for expected hallucinations, ERROR for unexpected exceptions
3. **Structured Logging**: Use `extra={}` parameter for structured data (URL, query, session ID)
4. **Performance**: Logging is async-safe and won't significantly impact performance

**Implementation**:
```python
import logging

logger = logging.getLogger(__name__)

# FR-003: Log hallucination at WARNING level
try:
    logger.warning(
        f"Hallucination detected - invalid resource: {url}",
        extra={
            "url": url,
            "title": resource_title,
            "query": query,
            "session_id": session_id
        }
    )
except Exception:
    # FR-009: Suppress logging failures
    pass

# FR-006: Log validation exception at ERROR level
try:
    logger.error(
        f"Validation exception for {url}: {exc}",
        extra={"url": url, "query": query},
        exc_info=True  # Include stack trace
    )
except Exception:
    # FR-009: Suppress logging failures
    pass
```

**Alternatives Considered**:
- **Custom logging methods in agent_logger**: Rejected - adds complexity, standard logging sufficient
- **Queue-based async logging**: Rejected - overkill, standard logging is already non-blocking
- **Fail loudly on logging errors**: Rejected - violates FR-009 requirement

---

### 3. Response Structure for Empty Results

**Question**: How to structure HTTP 404 error response to maintain consistency with existing error patterns?

**Research Findings**:

Existing error response pattern (from `src/api/schemas.py`):
```python
class ErrorResponse(BaseModel):
    error: str  # Human-readable message
    code: str   # Machine-readable code
    query: str  # Original user query
```

Used in:
- `GET /search`: Returns 400/503 with ErrorResponse
- `GET /nl/search`: Returns 400/503 with ErrorResponse
- `GET /resources/{uuid}`: Returns 400/404 with ErrorResponse

**Decision**: **Use existing `ErrorResponse` schema with HTTP 404 status**

**Rationale**:
1. **Consistency**: Matches existing error response pattern across all endpoints (Principle III: UX Consistency)
2. **No New Schemas**: Reuses existing `ErrorResponse` Pydantic model
3. **Machine-Readable**: `code: "NO_VALID_RESOURCES"` enables client-side error handling
4. **Actionable**: Message "no valid resources found" clearly indicates the issue

**Implementation**:
```python
if not validated_resources:
    raise HTTPException(
        status_code=404,
        detail=ErrorResponse(
            error="no valid resources found",
            code="NO_VALID_RESOURCES",
            query=query,
        ).model_dump(),
    )
```

**Alternatives Considered**:
- **Return empty array with 200**: Rejected - doesn't signal that resources existed but failed validation
- **Return 503 (Service Unavailable)**: Rejected - not a service failure, validation worked correctly
- **Custom error schema with validation details**: Rejected - leaks internal implementation, violates API contract simplicity

---

### 4. Filtering Implementation Location

**Question**: Where should resource filtering logic reside - in ReACT agent or endpoint handler?

**Research Findings**:

Current architecture:
- `ReACTAgent.run()`: Calls NL search, builds resource list, returns dict
- `run_experimental_agent()` (routes.py): Calls `agent.run()`, handles HTTP response

**Decision**: **Implement filtering in endpoint handler (`routes.py`), not in agent**

**Rationale**:
1. **Separation of Concerns**: Agent focuses on reasoning/tool use; endpoint handles HTTP-specific logic (404 responses)
2. **Testability**: Easier to test filtering logic separately from agent orchestration
3. **Isolation**: Keeps experimental endpoint changes isolated (per user constraint)
4. **Reusability**: Agent remains generic; different endpoints can apply different filtering strategies

**Implementation**:
```python
# In run_experimental_agent (routes.py)
result = agent.run(query=query, include_sources=include_sources)

if "resources" in result:
    validated_resources = []
    for resource in result["resources"]:
        is_valid = link_verifier.verify_link(resource["url"])
        if is_valid:
            validated_resources.append(resource)
        else:
            # Log hallucination
            ...

    if not validated_resources:
        # Return 404
        ...

    result["resources"] = validated_resources

return result
```

**Alternatives Considered**:
- **Filter in agent.run()**: Rejected - couples agent to HTTP semantics, harder to test
- **Create separate validation service**: Rejected - overkill for simple boolean check
- **Filter during resource search**: Rejected - search should remain independent of validation

---

## Best Practices Applied

### 1. Python Logging

- Use standard `logging` module (not print statements)
- WARNING level for expected issues (hallucinations)
- ERROR level for unexpected exceptions
- Include stack traces for exceptions (`exc_info=True`)
- Use `extra={}` for structured context

### 2. Exception Handling

- Catch broad `Exception` only when suppressing is required (FR-009)
- Never suppress exceptions silently without logging
- Return safe defaults (False) when validation fails
- Continue processing remaining items after individual failures

### 3. HTTP Status Codes

- 200: Success with valid resources
- 404: Not found (all resources failed validation)
- 400: Bad request (invalid input)
- 500: Server error (unexpected failures)

### 4. Type Safety

- All functions have explicit type hints
- Pydantic models validate data at runtime
- mypy enforces static type checking
- Use `bool` not `int` for True/False values

---

## Performance Considerations

### Expected Impact

- **Validation Time**: No change (same `link_verifier.verify_link()` call)
- **Filtering Overhead**: O(n) list iteration, negligible for n ≤ 3 resources
- **Logging Overhead**: <1ms per log entry, async-safe
- **Overall Impact**: <5% estimated increase in response time

### Optimization Opportunities

If performance degradation exceeds 10% (SC-004):
1. Batch validation calls
2. Cache validation results
3. Implement async validation with `asyncio.gather()`

**Current Decision**: Implement synchronous filtering first, optimize only if needed

---

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_agent_orchestrator.py`

- Test `_validate_resource_tool` returns `bool` (not string)
- Test exception handling returns `False`
- Test logging calls are made (with mocked logger)

### Integration Tests

**File**: `tests/integration/test_agent_api.py`

- Test mixed valid/invalid resources → only valid in response
- Test all invalid resources → HTTP 404 response
- Test validation exception → resource excluded
- Test logging failure suppression → no crash

### Contract Tests

**File**: `tests/contract/test_agent_contract.py`

- Test 404 response schema matches `contracts/agent-404.json`
- Test error response has correct fields (error, code, query)
- Test 404 code is "NO_VALID_RESOURCES"

---

## Open Questions (Resolved)

1. **Q**: Should we add a `NO_VALID_RESOURCES` error code to `AgentErrorCode` enum?
   **A**: Yes, add to maintain consistency with existing error code patterns.

2. **Q**: Should validation logging include the validation failure reason?
   **A**: Yes for exceptions (stack trace), not needed for simple False returns (URL is sufficient).

3. **Q**: Should we preserve resource order after filtering?
   **A**: Yes (FR-007), use list comprehension or filter that maintains order.

4. **Q**: What if search returns 0 resources (before validation)?
   **A**: Different from 404 scenario - return success with empty list (existing behavior unchanged).

---

## Summary

All research questions resolved with concrete decisions documented above. Key takeaways:

1. ✅ **Boolean return type**: Safe with DSPy, provides better type safety
2. ✅ **Standard logging with try/except**: Non-blocking, follows Python best practices
3. ✅ **Existing ErrorResponse schema**: Maintains API consistency
4. ✅ **Filter in endpoint handler**: Better separation of concerns, easier to test

No blockers identified. Proceed to Phase 1 design and implementation.
