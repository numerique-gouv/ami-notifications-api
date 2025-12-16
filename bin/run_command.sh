#!/bin/bash

# Only works when developping locally...
VAPID_PUBLIC_KEY_FILE="public_key.pem"
VAPID_PRIVATE_KEY_FILE="private_key.pem"
VAPID_APPLICATION_SERVER_KEY_FILE="applicationServerKey"
# Otherwise export it in your deployement config
export VAPID_PUBLIC_KEY=${VAPID_PUBLIC_KEY:-$(cat ${VAPID_PUBLIC_KEY_FILE})}
export VAPID_PRIVATE_KEY=${VAPID_PRIVATE_KEY:-$(cat ${VAPID_PRIVATE_KEY_FILE})}
export VAPID_APPLICATION_SERVER_KEY=${VAPID_APPLICATION_SERVER_KEY:-$(cat ${VAPID_APPLICATION_SERVER_KEY_FILE})}

if [ ! -z "$CONTAINER" ]
then
  # We're on scalingo, so automatically build the front app
  make build-app
  # Rebuild the FCM secret json keys file from the env vars, see the section in CONTRIBUTING.md
  echo "$FCM_KEYS_FILE" | base64 -d > "$GOOGLE_APPLICATION_CREDENTIALS"
fi

if [ ! -f .env.local ]
then
  # Create an empty file so uv won't fail on a missing file
  touch .env.local
  KEY=$(openssl rand -hex 32)
  echo "AUTH_COOKIE_JWT_SECRET=\"$KEY\"" >> .env.local
  KEY=$(openssl rand -hex 32)
  echo "PARTNERS_PSL_SECRET=\"$KEY\"" >> .env.local
fi

uv run --env-file .env --env-file .env.local litestar $*
