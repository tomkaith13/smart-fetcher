# Smart Fetcher

Smart tag-based resource fetcher using DSPy and FastAPI.

## Configuration

### Environment Variables

- `OLLAMA_HOST` - Ollama API endpoint (default: `http://localhost:11434`)
- `OLLAMA_MODEL` - Model name for semantic search (default: `gpt-oss:20b`)

For more details on Ollama health monitoring, see [specs/002-ollama-health-check/quickstart.md](specs/002-ollama-health-check/quickstart.md).

## Quick Start

```bash
make start
```

## Health Monitoring

The `/health` endpoint returns startup-time health status:
- **HTTP 200** with `status: healthy` - Ollama connected and model verified at startup
- **HTTP 200** with `status: degraded` - Ollama connected but model not running at startup
- **HTTP 503** with `status: unhealthy` - Ollama unreachable at startup

Health status is cached at service startup and does not change until restart. This ensures fast health checks (<100ms) without external dependency overhead.
