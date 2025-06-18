# Qwen Agent

A Python project using Poetry, uv, and venv for dependency and environment management.

## Project Structure

- `src/` — Main source code
- `tests/` — Test files
- `.venv/` — Virtual environment (excluded from git)
- `poetry.lock`, `uv.lock` — Dependency lock files (see below)

## Requirements

- Python 3.12+
- [Ollama](https://ollama.com/) must be installed and running locally for this project to function correctly. Follow the instructions on the Ollama website to install it for your operating system.

## Excluded Files (see `.gitignore`)

- `.venv/`, `venv/`, `ENV/` — Local virtual environments
- `__pycache__/`, `*.pyc` — Python bytecode
- `.env`, `.env.*` — Environment variables/secrets
- `.vscode/`, `.idea/` — Editor/IDE settings
- `*.log` — Log files
- `poetry.lock`, `uv.lock` — (Optional: include for reproducible installs, exclude for library projects)

## Getting Started

1. Install dependencies:
   ```sh
   poetry install
   ```
2. Run the main script:
   ```sh
   poetry run python src/qwen_agent.py
   ```
3. Run tests:
   ```sh
   poetry run pytest
   ```

## Notes
- Use `poetry add <package>` to add dependencies.
- Use `uv` for faster installs if desired.
- Do not commit sensitive files or local environment folders.

---

For more details, see the `.gitignore` file.