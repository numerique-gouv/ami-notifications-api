#!/bin/bash

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

# Only works when developping locally...
VAPID_PUBLIC_KEY_FILE="public_key.pem"
VAPID_PRIVATE_KEY_FILE="private_key.pem"
VAPID_APPLICATION_SERVER_KEY_FILE="applicationServerKey"
# Otherwise export it in your deployement config
export VAPID_PUBLIC_KEY=${VAPID_PUBLIC_KEY:-$(cat ${VAPID_PUBLIC_KEY_FILE})}
export VAPID_PRIVATE_KEY=${VAPID_PRIVATE_KEY:-$(cat ${VAPID_PRIVATE_KEY_FILE})}
export VAPID_APPLICATION_SERVER_KEY=${VAPID_APPLICATION_SERVER_KEY:-$(cat ${VAPID_APPLICATION_SERVER_KEY_FILE})}

if [ -z "$VAPID_PUBLIC_KEY" ] || [ -z "$VAPID_PRIVATE_KEY" ] || [ -z "$VAPID_APPLICATION_SERVER_KEY" ]
then
  echo "Missing keys, generating public_key.pem, private_key.pem and applicationServerKey now."
  # No key set yet, generate some local key files.
  uv run vapid-gen
  export VAPID_PUBLIC_KEY=$(cat ${VAPID_PUBLIC_KEY_FILE})
  export VAPID_PRIVATE_KEY=$(cat ${VAPID_PRIVATE_KEY_FILE})
  export VAPID_APPLICATION_SERVER_KEY=$(cat ${VAPID_APPLICATION_SERVER_KEY_FILE})
fi

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
