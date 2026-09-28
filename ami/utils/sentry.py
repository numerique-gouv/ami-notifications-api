import hashlib

import sentry_sdk
from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber


class CustomEventScrubber(EventScrubber):
    def __init__(self):
        denylist = DEFAULT_DENYLIST + [
            "birthcountry",
            "birthdate",
            "birthplace",
            "client_secret",
            "decoded_user_data",
            "decoded_userinfo",
            "family_name",
            "fc_hash",
            "gender",
            "given_name",
            "recipient_fc_hash",
            "userinfo_jws",
        ]
        super().__init__(denylist=denylist)


def add_counter(message_id: str):
    sentry_sdk.capture_message(
        message_id,
        level="info",
    )


def set_sentry_user(user):
    hashed_user_hash = hashlib.sha1(user.fc_hash.encode()).hexdigest()[:20]
    sentry_sdk.set_user({"id": hashed_user_hash})
