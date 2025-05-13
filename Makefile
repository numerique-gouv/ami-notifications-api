.PHONY: lint
lint:
	uv run ruff check --fix

.PHONY: format
format:
	uv run ruff format
	npx @biomejs/biome format --write

.PHONY: test
test:
	uv run --env-file .env.tests pytest

.PHONY: dev
dev:
	RELOAD="-r" DEBUG="--debug" HOSTNAME="127.0.0.1" bin/start.sh

.PHONY: serve
serve:
	bin/start.sh
