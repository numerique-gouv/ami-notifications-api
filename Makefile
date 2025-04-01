.PHONY: lint
lint:
	uv run ruff check --fix
	mypy src/

.PHONY: format
format:
	uv run ruff format

.PHONY: dev
dev:
	RELOAD="-r" HOSTNAME="127.0.0.1" bin/start.sh

.PHONY: serve
serve:
	bin/start.sh
