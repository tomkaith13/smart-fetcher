# Quickstart: Ollama Health

## Configure

- Environment variables:
  - `OLLAMA_HOST` (default: http://localhost:11434)
  - `OLLAMA_MODEL` (default: gpt-oss:20b)

## Verify Model (Makefile helpers planned)

- Check running models:
  - `make ollama-ps`
- Check specific model (replace):
  - `make ollama-check MODEL=gpt-oss:20b`

## Run

- Start the service (example):
  - `make run` or `python -m src.main`

## Health Endpoint

- `GET /health`
  - 200 healthy: Ollama connected and model verified at startup
  - 200 degraded: Ollama connected, model not verified at startup
  - 503 unhealthy: Ollama unreachable at startup

## Notes

- Health status is captured at startup and does not change until service restart.
- To refresh health status after changing Ollama/model state, restart the service.
