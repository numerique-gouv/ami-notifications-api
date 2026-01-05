ifdef CONTAINER
  # We're on scalingo, don't use uv
  RUN :=
else
  RUN := uv run --env-file .env --env-file .env.local
endif

.PHONY: install
install:
	npm ci

.PHONY: lint-and-format
lint-and-format: install
	uv run pre-commit run --all-files

.PHONY: test
test:
	$(RUN) pytest

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
	$(RUN) alembic upgrade head

.PHONY: publish-scheduled-notifications
publish-scheduled-notifications:
	bin/run_command.sh publish-scheduled-notifications

.PHONY: delete-published-scheduled-notifications
delete-published-scheduled-notifications:
	bin/run_command.sh delete-published-scheduled-notifications
