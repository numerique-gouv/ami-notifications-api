.PHONY: install
install:
	npm ci

.PHONY: lint-and-format
lint-and-format: install
	uv run pre-commit run --all-files
	npm run lint-and-format

.PHONY: test
test:
	uv run --env-file .env.tests pytest

.PHONY: dev
dev:
	RELOAD="-r" DEBUG="--debug" HOSTNAME="127.0.0.1" bin/start.sh

.PHONY: serve
serve:
	bin/start.sh
