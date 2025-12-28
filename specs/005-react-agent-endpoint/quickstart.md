# Quickstart: Experimental ReACT Agent Endpoint

## Endpoint
- URL: `POST /experimental/agent`
- Purpose: Single-turn agent using NL search + resource validation tools.
- Status: Experimental (responses avoid definitive claims when evidence is insufficient).
- Rate limit: 5 requests/min per user.

## Examples

### Ask a question
```bash
curl -sS -X POST http://localhost:8000/experimental/agent \
  -H 'Content-Type: application/json' \
  -d '{"query": "What is DSPy and how does it help with LLM tooling?"}'
```

### Ask for sources
```bash
curl -sS -X POST http://localhost:8000/experimental/agent \
  -H 'Content-Type: application/json' \
  -d '{"query": "Summarize the approach and include sources", "include_sources": true}'
```

### Handle long inputs safely
```bash
curl -sS -X POST http://localhost:8000/experimental/agent \
  -H 'Content-Type: application/json' \
  -d '{"query": "<long text>", "max_tokens": 1024}'
```

## Response Shapes
- Success (no citations): `{ "answer": "...", "query": "...", "meta": {"experimental": true} }`
- Success (citations): `{ "answer": "...", "query": "...", "citations": [...], "meta": {"experimental": true} }`
- Error: `{ "error": "...", "code": "TOOL_TIMEOUT|INTERNAL_ERROR", "query": "..." }`

## Notes
- Default LLM: Ollama model `gpt-oss:20b` via DSPy.
- Tool traces/logs are never exposed; internal only.
- Citations appear only when requested and validated.
- If the LLM provider is unavailable, the endpoint returns a limitation message (no stack trace).
