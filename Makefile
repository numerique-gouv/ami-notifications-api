ifdef CONTAINER
  # We're on scalingo, don't use uv
  RUN :=
else
  RUN := uv run
endif

.PHONY: install
install:
	npm ci

.PHONY: lint-and-format
lint-and-format: install
	$(RUN) pre-commit run --all-files

.PHONY: test
test:
	DJANGO_SETTINGS_MODULE=ami.settings $(RUN) pytest -vvv -ll --ff -x --reuse-db ami

.PHONY: test-create-db
test-create-db:
	DJANGO_SETTINGS_MODULE=ami.settings $(RUN) pytest -vvv -ll --ff -x --reuse-db ami --create-db

.PHONY: test-ci
test-ci:
	DJANGO_SETTINGS_MODULE=ami.settings $(RUN) pytest ami

.PHONY: statics
statics:
	$(RUN) python manage.py collectstatic

.PHONY: dev
dev:
	$(RUN) python manage.py runserver

.PHONY: serve
serve:
	$(RUN) python manage.py runserver

.PHONY: build-app
build-app:
	cd public/mobile-app && npm ci --include "dev" && npm run build

.PHONY: migrate
migrate:
	$(RUN) python manage.py migrate --fake-initial

.PHONY: publish-scheduled-notifications
publish-scheduled-notifications:
	bin/run_command.sh publish-scheduled-notifications

.PHONY: delete-published-scheduled-notifications
delete-published-scheduled-notifications:
	bin/run_command.sh delete-published-scheduled-notifications
