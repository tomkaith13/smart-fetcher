.PHONY: start ollama-ps ollama-check test test-unit test-integration test-contract

# Configurable defaults
LOG_LEVEL ?= info
HOST ?= 0.0.0.0
PORT ?= 8000

start:
	uv run uvicorn src.main:app --host $(HOST) --port $(PORT) --log-level $(LOG_LEVEL)

test:
	uv run pytest tests/ -v

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v

test-contract:
	uv run pytest tests/contract/ -v

ollama-ps:
	@echo "Listing running Ollama models..."
	@ollama ps

ollama-check:
	@if [ -z "$(MODEL)" ]; then \
		echo "Usage: make ollama-check MODEL=<model-name>"; \
		exit 1; \
	fi
	@echo "Checking if model '$(MODEL)' is running..."
	@ollama ps | grep -q "$(MODEL)" && echo "✓ Model '$(MODEL)' is running" || (echo "✗ Model '$(MODEL)' is NOT running" && exit 1)
