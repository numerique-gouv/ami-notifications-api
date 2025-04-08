#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"

VAPID_PRIVATE_KEY_FILE="private_key.pem"  # Only works when developping locally...
export VAPID_PRIVATE_KEY=${VAPID_PRIVATE_KEY:-$(cat ${VAPID_PRIVATE_KEY_FILE})}  # Otherwise export it in your deployement config

uv run litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD} ${DEBUG}
