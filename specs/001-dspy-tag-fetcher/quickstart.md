# Quickstart: Smart Tag-Based Resource Fetcher

## Prerequisites

1. **Python 3.13+** - Check with `python --version`
2. **uv package manager** - Install from [astral.sh/uv](https://astral.sh/uv)
3. **Ollama** - Install from [ollama.ai](https://ollama.ai)
4. **gpt-oss:20b model** - Pull with Ollama

## Setup

### 1. Install Ollama and Model

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama server
ollama serve

# In another terminal, pull the model
ollama pull gpt-oss:20b
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### 2. Install Python Dependencies

```bash
# From project root
uv sync
```

### 3. Run the Application

```bash
uv run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Verify Installation

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "ollama": "connected",
  "resources_loaded": 100
}
```

### Search by Tag

```bash
curl "http://localhost:8000/search?tag=home"
```

Expected response (semantic matches for "home"):
```json
{
  "results": [
    {
      "uuid": "...",
      "name": "...",
      "description": "...",
      "search_tag": "home"
    },
    {
      "uuid": "...",
      "name": "...",
      "description": "...",
      "search_tag": "residence"
    }
  ],
  "count": 2,
  "query": "home"
}
```

### Get Resource by UUID

```bash
curl http://localhost:8000/resources/{uuid}
```

### List All Resources

```bash
curl http://localhost:8000/resources
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Running Tests

```bash
# Fast suite (recommended during development): unit + contract
make test

# Full suite (includes integration):
make test-all

# Coverage (optional):
uv run pytest --cov=src --cov-report=term-missing

# Specific test types (optional):
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/contract/
```

## Linting and Type Checking

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy src/
```

## Troubleshooting

### Ollama Connection Failed

If you see `SERVICE_UNAVAILABLE` errors:

1. Ensure Ollama is running: `ollama serve`
2. Check the model is available: `ollama list`
3. Verify the API is reachable: `curl http://localhost:11434/api/tags`

### Model Not Found

If the gpt-oss:20b model isn't available:

```bash
ollama pull gpt-oss:20b
```

### Port Already in Use

If port 8000 is busy:

```bash
uv run uvicorn src.main:app --reload --port 8001
```

## Environment Variables (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `gpt-oss:20b` | Model to use for inference |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
