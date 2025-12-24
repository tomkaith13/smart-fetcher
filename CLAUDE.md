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

## Python Version

This project requires Python 3.13+ (specified in [.python-version](.python-version) and [pyproject.toml](pyproject.toml)).
