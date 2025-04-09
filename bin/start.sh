#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"

VAPID_PRIVATE_KEY_FILE="private_key.pem"  # Only works when developping locally...
export VAPID_PRIVATE_KEY=${VAPID_PRIVATE_KEY:-$(cat ${VAPID_PRIVATE_KEY_FILE})}  # Otherwise export it in your deployement config

curl -LsSf "https://astral.sh/uv/0.6.13/install.sh" | sh 2>&1

# Make the uv commands available
source "$HOME/.local/bin/env"


uv run litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD} ${DEBUG}
