#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"

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

if [ ! -z "$CONTAINER" ]
then
  # We're on scalingo, so automatically build the front app
  make build-app
else
  # We're on local dev, FranceConnect needs HTTPS so start backend server with SSL
  # On Scalingo, the backend is already on HTTPS
  SSL="${SSL:---ssl-keyfile=ssl-key.pem --ssl-certfile=ssl-cert.pem}"
fi

if [ ! -f .env.local ]
then
  # Create an empty file so uv won't fail on a missing file
  touch .env.local
fi

make migrate && uv run --env-file .env --env-file .env.local litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD} ${DEBUG} ${SSL}
