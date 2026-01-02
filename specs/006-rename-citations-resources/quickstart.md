# Quickstart: Rename Citations to Resources

**Feature**: Rename Citations to Resources in Agent Endpoint  
**Date**: 2026-01-01  
**Branch**: `006-rename-citations-resources`

## Overview

This refactoring renames the "citations" field to "resources" in the experimental agent endpoint response to align terminology with the rest of the API. This is a breaking change for the experimental endpoint but improves consistency.

## What Changed

### API Response Field Name
- **Before**: `{"answer": "...", "citations": [...]}`
- **After**: `{"answer": "...", "resources": [...]}`

### Schema Classes
- **Before**: `AgentAnswerWithCitations`, `Citation`
- **After**: `AgentAnswerWithResources`, `ResourceCitation`

### Request Parameters
- No change: `include_sources` parameter remains the same

## Quick Reference

### Making a Request

```bash
# Request with resources (include_sources=true)
curl -X POST http://localhost:8000/experimental/agent \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What resources do you have about hiking?",
    "include_sources": true
  }'
```

### Response Format (with resources)

```json
{
  "answer": "Based on available resources, hiking involves...",
  "query": "What resources do you have about hiking?",
  "meta": {
    "experimental": true
  },
  "resources": [
    {
      "title": "Hiking Guide",
      "url": "/resources/abc-123",
      "summary": "Comprehensive guide to hiking safety and equipment"
    }
  ]
}
```

### Response Format (without resources)

```json
{
  "answer": "Hiking involves...",
  "query": "What resources do you have about hiking?",
  "meta": {
    "experimental": true
  }
}
```

## Migration Guide

If you're consuming the experimental agent endpoint, update your code:

### Python

```python
# Before
response = requests.post("/experimental/agent", json={"query": "...", "include_sources": True})
data = response.json()
for citation in data.get("citations", []):
    print(citation["title"])

# After
response = requests.post("/experimental/agent", json={"query": "...", "include_sources": True})
data = response.json()
for resource in data.get("resources", []):
    print(resource["title"])
```

### JavaScript/TypeScript

```typescript
// Before
const response = await fetch("/experimental/agent", {
  method: "POST",
  body: JSON.stringify({ query: "...", include_sources: true })
});
const data = await response.json();
data.citations?.forEach(c => console.log(c.title));

// After
const response = await fetch("/experimental/agent", {
  method: "POST",
  body: JSON.stringify({ query: "...", include_sources: true })
});
const data = await response.json();
data.resources?.forEach(r => console.log(r.title));
```

## Testing

### Run All Tests

```bash
# Fast suite (unit + contract)
make test

# Full suite (includes integration)
make test-all
```

### Verify Contract Compliance

```bash
# Contract tests validate response schema
pytest tests/contract/test_agent_contract.py -v
```

### Integration Test

```bash
# Test actual API endpoint
pytest tests/integration/test_agent_api.py -v
```

## Files Changed

### Source Code
- `src/api/schemas.py` - Schema definitions
- `src/services/agent/react_agent.py` - Agent implementation
- `src/api/routes.py` - Endpoint documentation

### Tests
- `tests/contract/test_agent_contract.py` - Schema validation tests
- `tests/integration/test_agent_api.py` - API integration tests
- `tests/unit/test_agent_orchestrator.py` - Unit tests for agent logic

### Documentation
- `README.md` - API examples
- `specs/005-react-agent-endpoint/contracts/openapi.yaml` - OpenAPI specification (previous version)
- `specs/006-rename-citations-resources/contracts/openapi.yaml` - Updated OpenAPI specification

## Troubleshooting

### Tests failing with KeyError: 'resources'
**Cause**: Test is still checking for "citations" field  
**Fix**: Update test assertion to use "resources" instead

### mypy errors about AgentAnswerWithCitations
**Cause**: Import or type hint still uses old class name  
**Fix**: Update imports to use `AgentAnswerWithResources`

### API returns "citations" field
**Cause**: Code not fully updated or using cached response  
**Fix**: Verify all occurrences in `react_agent.py` are updated, restart server

## Next Steps

After merging this feature:
1. Update any external documentation referencing "citations"
2. Notify API consumers (if any) about the field rename
3. Update any monitoring/logging that references the old field name

## Related Specifications

- [Feature Specification](spec.md)
- [Implementation Plan](plan.md)
- [Data Model](data-model.md)
- [Research Notes](research.md)
