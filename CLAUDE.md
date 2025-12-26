# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**smart-fetcher** is a Python 3.13 project managed with `uv`, a modern Python package manager.

## Development Setup

This project uses `uv` instead of pip/poetry. All dependency and environment management should go through uv.

**Install dependencies:**
```bash
uv sync
```

**Run the application:**
```bash
uv run python main.py
```

**Add a new dependency:**
```bash
uv add <package-name>
```

**Add a development dependency:**
```bash
uv add --dev <package-name>
```

## Project Structure

Currently a single-file application with [main.py](main.py) as the entry point.

## Constitution & Development Standards

**All development work MUST comply with the project constitution** defined in [.specify/memory/constitution.md](.specify/memory/constitution.md).

Key principles to follow:
1. **Code Quality**: Type annotations required, functions <50 lines, ruff linting, comprehensive docstrings
2. **Testing Standards**: Comprehensive test coverage, organized in unit/integration/contract directories
3. **UX Consistency**: Consistent JSON structures, actionable error messages, proper HTTP codes

Quality gates that MUST pass before merge:
- `uv run pytest` (all tests passing)
- `uv run ruff check .` (zero errors)
- `uv run mypy src/` (zero type errors)
- `uv run ruff format --check .` (zero formatting violations)

## Python Version

This project requires Python 3.13+ (specified in [.python-version](.python-version) and [pyproject.toml](pyproject.toml)).

## Active Technologies
- Python 3.13 (specified in .python-version) + FastAPI, DSPy, Ollama (gpt-oss:20b), uvicorn, pydantic (001-dspy-tag-fetcher)
- In-memory (list/dict of Resource objects, deterministic seed) (001-dspy-tag-fetcher)

## Recent Changes
- 001-dspy-tag-fetcher: Added Python 3.13 (specified in .python-version) + FastAPI, DSPy, Ollama (gpt-oss:20b), uvicorn, pydantic
