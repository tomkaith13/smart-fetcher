# Quickstart: Testing Boolean Resource Validation

**Feature**: 007-bool-resource-validation
**Date**: 2026-01-04

## Overview

This guide provides step-by-step instructions for testing the boolean resource validation feature, including how to trigger hallucination scenarios, verify logging output, and test the HTTP 404 response.

## Prerequisites

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Start Ollama** (if testing with real LLM):
   ```bash
   # Ensure Ollama is running on localhost:11434
   ollama serve
   ```

3. **Set environment variables**:
   ```bash
   export OLLAMA_MODEL="gpt-oss:20b"
   export OLLAMA_HOST="http://localhost:11434"
   ```

## Running Tests

### 1. Run All Tests

```bash
# Run all tests (unit + integration + contract)
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### 2. Run Specific Test Suites

```bash
# Unit tests only (fast, no external dependencies)
uv run pytest tests/unit/

# Integration tests (may require Ollama)
uv run pytest tests/integration/

# Contract tests (API schema validation)
uv run pytest tests/contract/
```

### 3. Run Feature-Specific Tests

```bash
# Boolean validation unit tests
uv run pytest tests/unit/test_agent_orchestrator.py::test_validate_resource_returns_bool -v

# Filtering integration tests
uv run pytest tests/integration/test_agent_api.py::test_agent_filters_invalid_resources -v

# 404 contract test
uv run pytest tests/contract/test_agent_contract.py::test_agent_404_response_schema -v
```

## Manual Testing

### 1. Start the API Server

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Valid Resources (Happy Path)

```bash
curl -X POST http://localhost:8000/experimental/agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me resources about technology",
    "include_sources": true,
    "max_tokens": 1024
  }'
```

**Expected Response** (HTTP 200):
```json
{
  "answer": "...",
  "query": "show me resources about technology",
  "meta": {"experimental": true},
  "resources": [
    {
      "title": "...",
      "url": "...",
      "summary": "..."
    }
  ]
}
```

### 3. Test All Invalid Resources (404 Scenario)

To trigger the 404 response, you'll need to create a scenario where all resources fail validation. This can be done by:

**Option A**: Mock the link verifier to always return False (in tests)

**Option B**: Use a query that returns resources with invalid URLs (requires dataset manipulation)

**Example Test Request**:
```bash
curl -X POST http://localhost:8000/experimental/agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "nonexistent query that will fail validation",
    "include_sources": true,
    "max_tokens": 1024
  }' \
  -w "\nHTTP Status: %{http_code}\n"
```

**Expected Response** (HTTP 404):
```json
{
  "error": "no valid resources found",
  "code": "NO_VALID_RESOURCES",
  "query": "nonexistent query that will fail validation"
}
```

### 4. Verify Logging Output

```bash
# Run server with verbose logging
uv run uvicorn src.main:app --reload --log-level debug

# In another terminal, make requests and watch logs
tail -f logs/agent.log  # If file logging configured
```

**Expected Log Entries**:

**Hallucination (WARNING level)**:
```
WARNING: Hallucination detected - invalid resource: https://invalid-url.com
  Extra: {"url": "https://invalid-url.com", "title": "Invalid Resource", "query": "..."}
```

**Validation Exception (ERROR level)**:
```
ERROR: Validation exception for https://error-url.com: Connection timeout
  Extra: {"url": "https://error-url.com", "query": "..."}
  Traceback (most recent call last):
    ...
```

## Test Scenarios

### Scenario 1: Mixed Valid/Invalid Resources

**Setup**: Mock 5 resources (3 valid, 2 invalid)

**Test**:
```python
# In test file
def test_mixed_resources(mocker):
    # Mock link verifier to return: True, True, False, True, False
    mocker.patch.object(link_verifier, 'verify_link', side_effect=[True, True, False, True, False])

    response = client.post("/experimental/agent", json={
        "query": "test query",
        "include_sources": True
    })

    assert response.status_code == 200
    assert len(response.json()["resources"]) == 3  # Only valid ones
```

**Expected**:
- HTTP 200
- Response contains 3 resources
- 2 WARNING logs for invalid resources

### Scenario 2: All Resources Fail Validation

**Setup**: Mock all resources to fail validation

**Test**:
```python
def test_all_resources_invalid(mocker):
    # Mock link verifier to always return False
    mocker.patch.object(link_verifier, 'verify_link', return_value=False)

    response = client.post("/experimental/agent", json={
        "query": "test query",
        "include_sources": True
    })

    assert response.status_code == 404
    assert response.json()["error"] == "no valid resources found"
    assert response.json()["code"] == "NO_VALID_RESOURCES"
```

**Expected**:
- HTTP 404
- Error response with correct schema
- Multiple WARNING logs (one per invalid resource)

### Scenario 3: Validation Exception Handling

**Setup**: Mock link verifier to throw exception

**Test**:
```python
def test_validation_exception(mocker):
    # Mock link verifier to throw exception
    mocker.patch.object(link_verifier, 'verify_link', side_effect=ConnectionError("Timeout"))

    response = client.post("/experimental/agent", json={
        "query": "test query",
        "include_sources": True
    })

    assert response.status_code == 404  # Treated as all invalid
    assert response.json()["error"] == "no valid resources found"
```

**Expected**:
- HTTP 404 (all resources treated as invalid)
- ERROR log with stack trace
- No server crash

### Scenario 4: Logging Failure Suppression

**Setup**: Mock logger to throw exception

**Test**:
```python
def test_logging_failure_suppressed(mocker):
    # Mock logger.warning to throw exception
    mocker.patch('src.api.routes.logger.warning', side_effect=Exception("Logger failed"))

    # Mock some invalid resources
    mocker.patch.object(link_verifier, 'verify_link', return_value=False)

    response = client.post("/experimental/agent", json={
        "query": "test query",
        "include_sources": True
    })

    # Request should still complete successfully (or with 404)
    assert response.status_code in [200, 404]
    # No server crash despite logging failure
```

**Expected**:
- Request completes (doesn't crash)
- Logging failure is suppressed
- Resource still filtered correctly

## Debugging Tips

### 1. Enable Verbose Logging

```python
# In test file
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Check Test Coverage

```bash
uv run pytest --cov=src --cov-report=term-missing
```

Look for:
- `src/services/agent/react_agent.py`: Lines 136-162 (validate function)
- `src/api/routes.py`: Lines 206-250 (filtering logic)

### 3. Isolate Failing Tests

```bash
# Run single test with verbose output
uv run pytest tests/integration/test_agent_api.py::test_agent_filters_invalid_resources -vv -s
```

### 4. Mock External Dependencies

Always mock:
- `LinkVerifier.verify_link()` - to control validation results
- `NLSearchService.search()` - to control resource candidates
- `dspy.ReAct` - to avoid needing Ollama for unit tests

## Quality Gates

Before merging, ensure:

1. **All tests pass**:
   ```bash
   uv run pytest
   ```

2. **No linting errors**:
   ```bash
   uv run ruff check .
   ```

3. **No type errors**:
   ```bash
   uv run mypy src/
   ```

4. **Formatting is correct**:
   ```bash
   uv run ruff format --check .
   ```

## Next Steps

1. Review test output for any failures
2. Check coverage report for untested code paths
3. Verify logging output matches expectations
4. Test edge cases (empty queries, network timeouts, etc.)
5. Run full integration test suite with real Ollama backend
