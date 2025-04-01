#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"

uv run litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD}
