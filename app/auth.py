import datetime
from base64 import urlsafe_b64encode
from uuid import uuid4


def generate_nonce() -> str:
    """Generate a NONCE by concatenating:
    - a uuid4 (for randomness and high confidence of uniqueness)
    - the curent timestamp (for sequentiality)

    The result is then base64 encoded.

    """
    uuid = uuid4()
    now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    return urlsafe_b64encode(f"{uuid}-{now}".encode("utf8")).decode("utf8")
