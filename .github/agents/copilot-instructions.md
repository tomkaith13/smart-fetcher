# smart-fetcher Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-26

## Active Technologies
- Python 3.13 + Faker (existing), Pydantic (existing), pytest (existing) (003-expand-dataset)
- In-memory (ResourceStore class, no persistence required) (003-expand-dataset)
- Python 3.13 (per pyproject requires-python >=3.13) + FastAPI, Uvicorn, Pydantic v2, DSPy, httpx (001-nl-uuid-search)
- In-memory `ResourceStore` seeded with canonical resources (UUID/title/summary/tags) (001-nl-uuid-search)
- N/A (in-memory session for single-turn) (005-react-agent-endpoint)

- Python 3.11+ + FastAPI, Pydantic v2, httpx (already used), subprocess (stdlib), pytes (002-ollama-health-check)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11+: Follow standard conventions

## Recent Changes
- 005-react-agent-endpoint: Added Python 3.13
- 005-react-agent-endpoint: Added Python 3.11
- 001-nl-uuid-search: Added Python 3.13 (per pyproject requires-python >=3.13) + FastAPI, Uvicorn, Pydantic v2, DSPy, httpx


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
