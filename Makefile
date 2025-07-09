.PHONY: install
install:
	npm ci

.PHONY: lint-and-format
lint-and-format: install
	uv run pre-commit run --all-files

.PHONY: test
test:
	uv run --env-file .env pytest

.PHONY: dev
dev:
	RELOAD="-r" DEBUG="--debug" HOSTNAME="0.0.0.0" bin/start.sh

.PHONY: serve
serve:
	bin/start.sh

.PHONY: build-app
build-app:
	cd public/mobile-app && npm ci --include "dev" && npm run build

.PHONY: migrate
migrate:
	uv run --env-file .env alembic upgrade head
