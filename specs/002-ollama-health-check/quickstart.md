# Quickstart: Ollama Health

## Configure

- Environment variables:
  - `OLLAMA_HOST` (default: http://localhost:11434)
  - `OLLAMA_MODEL` (default: gpt-oss:20b)

## Verify Model

Check running models:
```bash
make ollama-ps
```

Check specific model:
```bash
make ollama-check MODEL=gpt-oss:20b
```

## Run

Start the service:
```bash
make start
```

## Health Endpoint

`GET /health` returns startup-time health status:
- **200 healthy**: Ollama connected and model verified at startup
- **200 degraded**: Ollama connected, model not verified at startup
- **503 unhealthy**: Ollama unreachable at startup

## Notes

- Health status is captured once at startup and persists until service restart.
- To refresh health status after changing Ollama/model state, restart the service.
- The endpoint does not perform live checks, ensuring fast response times (<100ms).
