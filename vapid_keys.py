import os
from pathlib import Path

import webpush.cli as webpush_cli

# VAPID_PUBLIC_KEY_FILE="public_key.pem"
# VAPID_PRIVATE_KEY_FILE="private_key.pem"
# VAPID_APPLICATION_SERVER_KEY_FILE="applicationServerKey"
# # Otherwise export it in your deployement config
# export VAPID_PUBLIC_KEY=${VAPID_PUBLIC_KEY:-$(cat ${VAPID_PUBLIC_KEY_FILE})}
# export VAPID_PRIVATE_KEY=${VAPID_PRIVATE_KEY:-$(cat ${VAPID_PRIVATE_KEY_FILE})}
# export VAPID_APPLICATION_SERVER_KEY=${VAPID_APPLICATION_SERVER_KEY:-$(cat ${VAPID_APPLICATION_SERVER_KEY_FILE})}

# if [ -z "$VAPID_PUBLIC_KEY" ] || [ -z "$VAPID_PRIVATE_KEY" ] || [ -z "$VAPID_APPLICATION_SERVER_KEY" ]
# then
#   echo "Missing keys, generating public_key.pem, private_key.pem and applicationServerKey now."
#   # No key set yet, generate some local key files.
#   uv run vapid-gen
#   export VAPID_PUBLIC_KEY=$(cat ${VAPID_PUBLIC_KEY_FILE})
#   export VAPID_PRIVATE_KEY=$(cat ${VAPID_PRIVATE_KEY_FILE})
#   export VAPID_APPLICATION_SERVER_KEY=$(cat ${VAPID_APPLICATION_SERVER_KEY_FILE})
#


def keys_in_env() -> bool:
    return (
        bool(os.getenv("VAPID_PUBLIC_KEY"))
        and bool(os.getenv("VAPID_PRIVATE_KEY"))
        and bool(os.getenv("VAPID_APPLICATION_SERVER_KEY"))
    )


def load_from_env(config: dict[str, str]) -> dict[str, str]:
    config["VAPID_PUBLIC_KEY"] = os.getenv("VAPID_PUBLIC_KEY", "")
    config["VAPID_PRIVATE_KEY"] = os.getenv("VAPID_PRIVATE_KEY", "")
    config["VAPID_APPLICATION_SERVER_KEY"] = os.getenv("VAPID_APPLICATION_SERVER_KEY", "")
    return config


def keys_on_disk() -> bool:
    return (
        Path("public_key.pem").exists()
        and Path("private_key.pem").exists()
        and Path("applicationServerKey").exists()
    )


def read_from_file(key_file: str) -> str:
    with open(key_file, "r") as keyfile:
        return keyfile.read()


def load_from_disk(config: dict[str, str]) -> dict[str, str]:
    config["VAPID_PUBLIC_KEY"] = read_from_file("public_key.pem")
    config["VAPID_PRIVATE_KEY"] = read_from_file("private_key.pem")
    config["VAPID_APPLICATION_SERVER_KEY"] = read_from_file("applicationServerKey")
    return config


def initialize(config: dict[str, str]) -> dict[str, str]:
    if keys_in_env():
        return load_from_env(config)
    if keys_on_disk():
        return load_from_disk(config)
    webpush_cli.main()  # Generate key files on the disk.
    return load_from_disk(config)
