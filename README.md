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
