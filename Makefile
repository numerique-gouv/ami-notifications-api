ifdef CONTAINER
  # We're on scalingo, don't use uv
  RUN :=
else
  RUN := uv run
endif

ssl-key.pem:
	# Generate some local SSL certs for development
	openssl req -x509 -newkey rsa:4096 -keyout ssl-key.pem -out ssl-cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"

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
	$(RUN) python manage.py compilescss
	$(RUN) python manage.py collectstatic --noinput

.PHONY: dev
dev: ssl-key.pem
	$(RUN) uvicorn ami.asgi:application --reload --ssl-keyfile ssl-key.pem --ssl-certfile ssl-cert.pem --host localhost --port 8000

.PHONY: build-app
build-app:
	cd public/mobile-app && npm ci --include "dev" && npm run build

.PHONY: migrate
migrate:
	$(RUN) python manage.py migrate --fake-initial

.PHONY: publish-scheduled-notifications
publish-scheduled-notifications:
	$(RUN) python manage.py publish-scheduled-notifications

.PHONY: delete-published-scheduled-notifications
delete-published-scheduled-notifications:
	$(RUN) python manage.py delete-published-scheduled-notifications

.PHONY: replicate-anonymized-data
replicate-anonymized-data:
	$(RUN) python manage.py replicate-anonymized-data
