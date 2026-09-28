import hashlib

import sentry_sdk


def add_counter(message_id: str):
    sentry_sdk.capture_message(
        message_id,
        level="info",
    )


def set_sentry_user(user):
    hashed_user_hash = hashlib.sha1(user.fc_hash.encode()).hexdigest()[:20]
    sentry_sdk.set_user({"id": hashed_user_hash})
