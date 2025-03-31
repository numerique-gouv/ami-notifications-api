PHONY: lint format

lint:
	uv run ruff check --fix
	mypy src/

format:
	uv run ruff format
