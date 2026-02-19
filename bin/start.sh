#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="0.0.0.0"

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
  # We're on scalingo, so automatically build the front app
  make build-app
  # Rebuild the FCM secret json keys file from the env vars, see the section in CONTRIBUTING.md
  echo "$FCM_KEYS_FILE" | base64 -d > "$GOOGLE_APPLICATION_CREDENTIALS"
else
  # We're on local dev, FranceConnect needs HTTPS so start backend server with SSL
  # On Scalingo, the backend is already on HTTPS
  if [ ! -f ssl-key.pem ]
  then
    openssl req -x509 -newkey rsa:4096 -keyout ssl-key.pem -out ssl-cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"
  fi
  SSL="${SSL:---ssl-keyfile=ssl-key.pem --ssl-certfile=ssl-cert.pem}"
fi

if [ ! -z "$CONTAINER" ]
then
  # We're on scalingo, don't use uv
  RUN=""
else
  if [ ! -f .env.local ]
  then
    # Create an empty file so uv won't fail on a missing file
    touch .env.local
    KEY=$(openssl rand -hex 32)
    echo "AUTH_COOKIE_JWT_SECRET=\"$KEY\"" >> .env.local
    KEY=$(openssl rand -hex 32)
    echo "PARTNERS_PSL_SECRET=\"$KEY\"" >> .env.local
  fi

  RUN="uv run --env-file .env --env-file .env.local"
fi

make migrate && ${RUN} litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD} ${DEBUG} ${SSL}
