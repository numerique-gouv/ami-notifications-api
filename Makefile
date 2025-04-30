.PHONY: lint
lint:
	uv run ruff check --fix
	mypy src/

.PHONY: format
format:
	uv run ruff format

.PHONY: test
test:
	uv run pytest

.PHONY: dev
dev:
	RELOAD="-r" DEBUG="--debug" HOSTNAME="127.0.0.1" ENV_FILE="--env-file .env" bin/start.sh

.PHONY: serve
serve:
	bin/start.sh

update_deps:
	uv export --output-file requirements.txt --no-dev --no-emit-project --frozen
