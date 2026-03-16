# Repository Guidelines

## Project Structure & Module Organization
This repository is intentionally small. Keep all logic within `main.py`.

## Build, Test, and Development Commands
- `uv sync`: install deps.
- `uv run python main.py <file>`: decrypt a backup file.
- `uv run python main.py -p <password> <file>`: decrypt a backup file with custom password.
- `uv run ruff format`: run formatter.
- `uv run ruff check`: run formatter.
- `uv run pytest`: run tests.