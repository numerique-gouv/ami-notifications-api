#!/bin/bash

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

if [ "$APP" == "ami-back-prod" ]
then
  # We don't want to use the FranceConnect proxy in production
  export PUBLIC_FC_PROXY=""
fi

if [ ! -z "$CONTAINER" ]
then
  # We're running on Scalingo
  # Rebuild the FCM secret json keys file from the env vars, see the section in CONTRIBUTING.md
  echo "$FCM_KEYS_FILE" | base64 -d > "$GOOGLE_APPLICATION_CREDENTIALS"
  # Don't use uv
  RUN=""
fi

make migrate && gunicorn ami.asgi:application --bind ${HOST}:${PORT} --worker-class uvicorn.workers.UvicornWorker --forwarded-allow-ips="*" --log-file -
