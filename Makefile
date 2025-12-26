.PHONY: start ollama-ps ollama-check

start:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

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
