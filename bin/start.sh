#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"

curl -LsSf "https://astral.sh/uv/0.6.1/install.sh" | sh 2>&1

# Make the uv commands available
source "$HOME/.local/bin/env"

uv run litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD}
