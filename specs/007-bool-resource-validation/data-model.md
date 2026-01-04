# Data Model: Boolean Resource Validation

**Feature**: 007-bool-resource-validation
**Date**: 2026-01-04

## Overview

This document describes the data structures and type changes required for implementing boolean resource validation with hallucination filtering.

## Modified Data Structures

### 1. Validation Function Return Type

**File**: `src/services/agent/react_agent.py`

**Current Implementation**:
```python
def _validate_resource_tool(self, url: str) -> str:
    """Tool function for resource validation (called by DSPy ReAct).

    Returns:
        String describing validation result.
    """
    is_valid = self.link_verifier.verify_link(url)
    return f"Resource {url} is {'valid' if is_valid else 'invalid or unreachable'}"
```

**New Implementation**:
```python
def _validate_resource_tool(self, url: str) -> bool:
    """Tool function for resource validation (called by DSPy ReAct).

    Args:
        url: Resource URL to validate.

    Returns:
        Boolean: True if resource is valid, False if hallucinated/invalid.

    Raises:
        Exception: Logged as ERROR, resource treated as invalid.
    """
    try:
        is_valid = self.link_verifier.verify_link(url)

        # Log validation result
        if not is_valid:
            self.logger.warning(
                f"Hallucination detected - invalid resource: {url}",
                extra={"url": url, "session_id": self.current_session_id}
            )

        return is_valid
    except Exception as e:
        # FR-006: Exception handling - treat as invalid, log at ERROR level
        self.logger.error(
            f"Validation exception for resource {url}: {e}",
            extra={"url": url, "session_id": self.current_session_id},
            exc_info=True
        )
        return False
```

**Key Changes**:
- Return type: `str` → `bool`
- Return value: Descriptive string → `True`/`False`
- Added exception handling with ERROR logging (FR-006)
- Added hallucination logging at WARNING level (FR-003)
- Added try/except to suppress logging failures (FR-009 handled in logger)

### 2. Resource Filtering Logic

**File**: `src/api/routes.py` (in `run_experimental_agent` function)

**Current Implementation** (lines 206-215):
```python
if include_sources:
    resource_items, _, _, _ = self.nl_search_service.search(query)
    for item in resource_items[:3]:  # Top 3 results
        is_valid = self.link_verifier.verify_link(item.link)
        if is_valid:
            resources.append(
                ResourceCitation(
                    title=item.name,
                    url=item.link,
                    summary=item.summary,
                )
            )
```

**New Implementation**:
```python
if include_sources:
    resource_items, _, _, _ = self.nl_search_service.search(query)

    # FR-002, FR-005: Filter resources using boolean validation
    validated_resources = []
    for item in resource_items[:3]:  # Top 3 results
        try:
            is_valid = self.link_verifier.verify_link(item.link)

            if not is_valid:
                # FR-003: Log hallucination at WARNING level
                try:
                    logger.warning(
                        f"Hallucination detected - invalid resource: {item.link}",
                        extra={"url": item.link, "title": item.name, "query": query}
                    )
                except Exception:
                    # FR-009: Suppress logging failures
                    pass
            else:
                # FR-007: Preserve order of valid resources
                validated_resources.append(
                    ResourceCitation(
                        title=item.name,
                        url=item.link,
                        summary=item.summary,
                    )
                )
        except Exception as e:
            # FR-006: Validation exception - treat as invalid, log at ERROR
            try:
                logger.error(
                    f"Validation exception for {item.link}: {e}",
                    extra={"url": item.link, "query": query},
                    exc_info=True
                )
            except Exception:
                # FR-009: Suppress logging failures
                pass

    # FR-008: Return 404 if all resources failed validation
    if not validated_resources:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error="no valid resources found",
                code="NO_VALID_RESOURCES",
                query=query,
            ).model_dump(),
        )

    resources = validated_resources
```

**Key Changes**:
- Added `validated_resources` list to track valid resources only
- Validation failures logged at WARNING level (FR-003)
- Validation exceptions logged at ERROR level with stack trace (FR-006)
- All logging wrapped in try/except to suppress failures (FR-009)
- Returns HTTP 404 if all resources invalid (FR-008)
- Preserves order of valid resources (FR-007)

### 3. Error Response Schema

**File**: `src/api/schemas.py`

**Current Error Codes**:
```python
class AgentErrorCode(str, Enum):
    """Error codes for agent endpoint."""
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

**New Error Code** (if not already covered by ErrorResponse):
```python
class AgentErrorCode(str, Enum):
    """Error codes for agent endpoint."""
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NO_VALID_RESOURCES = "NO_VALID_RESOURCES"  # NEW: All resources failed validation
```

**Existing ErrorResponse Schema** (used for 404):
```python
class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str  # "no valid resources found"
    code: str   # "NO_VALID_RESOURCES"
    query: str  # Original user query
```

## Data Flow

### Validation Flow

```
User Request (include_sources=true)
    ↓
Search for Resources (NLSearchService)
    ↓
For Each Resource:
    ├─→ Validate URL (link_verifier.verify_link)
    │   ├─→ Returns True → Add to validated_resources
    │   └─→ Returns False → Log WARNING, skip resource
    │
    └─→ Exception During Validation
        └─→ Log ERROR (with stack trace), treat as False, skip resource
    ↓
Check validated_resources list:
    ├─→ Empty (all failed) → Return HTTP 404 with ErrorResponse
    └─→ Has items → Return HTTP 200 with resources in response
```

### Logging Flow

```
Validation Result:
    ├─→ is_valid == False (hallucination)
    │   └─→ logger.warning(message, extra={url, title, query})
    │       └─→ [try/except suppresses logging failures]
    │
    └─→ Exception during validation
        └─→ logger.error(message, extra={url, query}, exc_info=True)
            └─→ [try/except suppresses logging failures]
```

## Type Safety

All changes maintain type safety with Python 3.13 type hints:

- `_validate_resource_tool(url: str) -> bool` (previously `-> str`)
- `validated_resources: list[ResourceCitation]` (new variable)
- `is_valid: bool` (existing, unchanged)
- All Pydantic models validated at runtime

## Testing Data

### Test Scenarios

1. **Valid Resources Only**
   - Input: 3 resources, all valid
   - Expected: HTTP 200, all 3 in response

2. **Mixed Valid/Invalid**
   - Input: 5 resources (3 valid, 2 invalid)
   - Expected: HTTP 200, only 3 valid in response, 2 WARNING logs

3. **All Invalid**
   - Input: 3 resources, all invalid
   - Expected: HTTP 404, error="no valid resources found", 3 WARNING logs

4. **Validation Exception**
   - Input: 1 resource, validation throws exception
   - Expected: HTTP 404 (if only resource), 1 ERROR log with stack trace

5. **Logging Failure**
   - Input: Validation fails, logger.warning throws exception
   - Expected: Resource still filtered, no crash, suppressed logging error

## Dependencies

**Unchanged**:
- `LinkVerifier.verify_link(url: str) -> bool` (already returns bool)
- `ResourceCitation` Pydantic model
- `ErrorResponse` Pydantic model
- `AgentErrorCode` enum (extended with NO_VALID_RESOURCES)

**Modified**:
- `_validate_resource_tool` return type only
- Filtering logic in `run_experimental_agent` endpoint
