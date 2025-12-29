# Smart Fetcher

Smart tag-based resource fetcher using DSPy and FastAPI.

## Dataset

The service includes a synthetic test dataset for semantic search testing:
- **500 resources** with contextually appropriate content
- **12 tag categories**: home, car, technology, food, health, finance, travel, education, sports, music, fashion, nature
- **Minimum 40 resources per tag** for comprehensive tag coverage
- **Deterministic generation** with fixed seed for reproducibility
- **Tag-specific content generators** for semantic variety (e.g., "home" tags get house-related content)

Dataset generation takes <100ms and produces unique, schema-validated resources on service startup.

For dataset expansion details, see [specs/003-expand-dataset/](specs/003-expand-dataset/).

## Configuration

### Environment Variables

- `OLLAMA_HOST` - Ollama API endpoint (default: `http://localhost:11434`)
- `OLLAMA_MODEL` - Model name for semantic search and agent (default: `gpt-oss:20b`)
- `NL_SEARCH_RESULT_CAP` - Maximum results for NL search (default: `5`)
- `AGENT_TIMEOUT_SEC` - Agent execution timeout in seconds (default: `5`)
- `AGENT_MAX_TOKENS` - Maximum tokens for agent response (default: `1024`)

For more details on Ollama health monitoring, see [specs/002-ollama-health-check/quickstart.md](specs/002-ollama-health-check/quickstart.md).

For NL UUID search feature details, see [specs/004-nl-uuid-search/](specs/004-nl-uuid-search/).

## Quick Start

```bash
make start
```

## Testing

Use Make targets to control test scope:

```bash
# Fast suite: unit + contract (no integration)
make test

# Full suite: unit + contract + integration
make test-all

# Optional: lint, format, types
ruff check .
ruff format src/ tests/
mypy src/
```

## Health Monitoring

The `/health` endpoint returns startup-time health status:
- **HTTP 200** with `status: healthy` - Ollama connected and model verified at startup
- **HTTP 200** with `status: degraded` - Ollama connected but model not running at startup
- **HTTP 503** with `status: unhealthy` - Ollama unreachable at startup

Health status is cached at service startup and does not change until restart. This ensures fast health checks (<100ms) without external dependency overhead.

## API Endpoints

### Experimental Agent Endpoint (ReACT)

**⚠️ Experimental Feature**: This endpoint uses a ReACT-style agent to answer questions by automatically searching and validating resources.

Ask a question and get a direct AI-generated answer:

```bash
curl -s -X POST "http://localhost:8000/experimental/agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is DSPy and how does it help with LLM tooling?"}' | jq
```

Request with validated sources/citations:

```bash
curl -s -X POST "http://localhost:8000/experimental/agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about hiking", "include_sources": true}' | jq
```

**Agent Behavior**:
- Uses `gpt-oss:20b` model via Ollama by default
- Automatically calls NL search and resource validation tools
- Returns only the final answer (tool traces are logged internally)
- Includes citations only when `include_sources=true`
- Provides helpful limitation messages when evidence is insufficient

**Response Structure**:
- Success: `{answer, query, meta: {experimental: true}, citations?: [...]}`
- Error: `{error, code, query}`

For more details, see [specs/005-react-agent-endpoint/quickstart.md](specs/005-react-agent-endpoint/quickstart.md).

### Natural Language Search

Search for resources using natural language queries:

```bash
curl -s "http://localhost:8000/nl/search?q=hiking" | jq
```

Returns JSON-wrapped results with verified internal deep links:
- `results`: Array of resource items (uuid, name, summary, link, tags)
- `count`: Number of results
- `query`: Original query echoed back
- `message`: Optional guidance for no-match/ambiguity
- `candidate_tags`: Suggested tags for refinement

### Tag-Based Search

Search resources by semantic tag:

```bash
curl -s "http://localhost:8000/search?tag=home" | jq
```

### Resource Retrieval

Get a specific resource by UUID:

```bash
curl -s "http://localhost:8000/resources/{uuid}" | jq
```

List all resources:

```bash
curl -s "http://localhost:8000/resources" | jq
```
