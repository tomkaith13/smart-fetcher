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
make start
```

You can customize the host, port, and log level:
```bash
make start HOST=127.0.0.1 PORT=8080 LOG_LEVEL=debug
```

**Add a new dependency:**
```bash
uv add <package-name>
```

**Add a development dependency:**
```bash
uv add --dev <package-name>
```

## Git Workflow

**All tasks from any plan MUST start with their own git branch if the current branch is main.**

## Project Structure

Currently a single-file application with [main.py](main.py) as the entry point.

## Constitution & Development Standards

**All development work MUST comply with the project constitution** defined in [.specify/memory/constitution.md](.specify/memory/constitution.md).

Key principles to follow:
1. **Code Quality**: Type annotations required, functions <50 lines, ruff linting, comprehensive docstrings
2. **Testing Standards**: Comprehensive test coverage, organized in unit/integration/contract directories. **Do not add unnecessary tests - stick to functional requirements alone.**
3. **UX Consistency**: Consistent JSON structures, actionable error messages, proper HTTP codes

Quality gates that MUST pass before merge:
- `make test` (all unit and contract tests passing)
- `make lint` (zero linting errors)
- `make check` (zero type errors)
- `make format` followed by checking for uncommitted changes (zero formatting violations)

Available test targets:
- `make test` - Run unit and contract tests (fast)
- `make test-all` - Run all tests including integration tests
- `make test-unit` - Run only unit tests
- `make test-integration` - Run only integration tests
- `make test-contract` - Run only contract tests

## Python Version

This project requires Python 3.13+ (specified in [.python-version](.python-version) and [pyproject.toml](pyproject.toml)).

## Active Technologies
- Python 3.13 (specified in .python-version) + FastAPI, DSPy, Ollama (gpt-oss:20b), uvicorn, pydantic (001-dspy-tag-fetcher)
- In-memory (list/dict of Resource objects, deterministic seed) (001-dspy-tag-fetcher)
- Python 3.13 + FastAPI 0.115+, DSPy 2.5+, Pydantic 2.10+ (007-bool-resource-validation)
- In-memory (deterministic seed-based resource generation) (007-bool-resource-validation)

## Recent Changes
- 001-dspy-tag-fetcher: Added Python 3.13 (specified in .python-version) + FastAPI, DSPy, Ollama (gpt-oss:20b), uvicorn, pydantic
