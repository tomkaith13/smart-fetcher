# Data Model (Experimental ReACT Agent Endpoint)

## Entities

### Query
- Fields:
  - `text: string` (required)
  - `include_sources: boolean` (optional, default false)
  - `max_tokens: integer` (optional; safety cap)
- Validation:
  - `text` length 1..4000 (configurable)
  - `text` must pass safety filters (no harmful content)

### AgentSession
- Fields:
  - `id: UUID`
  - `started_at: datetime`
  - `ended_at: datetime`
  - `status: enum {"success","no_evidence","tool_error","timeout"}`
- Relationships:
  - Has many `ToolAction`

### ToolAction
- Fields:
  - `tool: enum {"nl_search","validate_resource"}`
  - `params: object`
  - `result_summary: string`
  - `timestamp: datetime`
- Relationships:
  - Belongs to `AgentSession`

### Resource
- Fields:
  - `title: string`
  - `url: string`
  - `summary: string`
- Validation:
  - `url` must be valid and reachable (HTTP/HTTPS)

### ValidationResult
- Fields:
  - `resource_url: string`
  - `is_valid: boolean`
  - `reason: string`
  - `timestamp: datetime`

## Response Shapes

### Success (no citations)
```json
{
  "answer": "...",
  "query": "...",
  "meta": {"experimental": true}
}
```

### Success (with citations)
```json
{
  "answer": "...",
  "query": "...",
  "citations": [
    {"title": "...", "url": "...", "summary": "..."}
  ],
  "meta": {"experimental": true}
}
```

### Error
```json
{
  "error": "<human-readable>",
  "code": "<MACHINE_CODE>",
  "query": "..."
}
```
