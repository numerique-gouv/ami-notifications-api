PHONY: lint format dev

lint:
	uv run ruff check --fix
	mypy src/

format:
	uv run ruff format

dev:
	uv run litestar run -r
