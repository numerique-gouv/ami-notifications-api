.PHONY: install
install:
	npm ci

.PHONY: lint-and-format
lint-and-format: install
	uv run pre-commit run --all-files

.PHONY: test
test:
	DJANGO_SETTINGS_MODULE=ami.settings uv run pytest ami

.PHONY: dev
dev:
	uv run manage.py runserver --settings=ami.settings

.PHONY: serve
serve:
	uv run manage.py runserver --settings=ami.settings

.PHONY: build-app
build-app:
	cd public/mobile-app && npm ci --include "dev" && npm run build

.PHONY: migrate
migrate:
	uv run manage.py migrate --fake-initial

.PHONY: publish-scheduled-notifications
publish-scheduled-notifications:
	bin/run_command.sh publish-scheduled-notifications

.PHONY: delete-published-scheduled-notifications
delete-published-scheduled-notifications:
	bin/run_command.sh delete-published-scheduled-notifications
