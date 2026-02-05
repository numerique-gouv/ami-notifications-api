import sentry_sdk


def add_counter(message_id: str):
    sentry_sdk.capture_message(
        message_id,
        level="info",
    )
