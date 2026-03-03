from base64 import urlsafe_b64encode
from uuid import uuid4

from django.utils.timezone import now


def generate_nonce() -> str:
    """Generate a NONCE by concatenating:
    - a uuid4 (for randomness and high confidence of uniqueness)
    - the curent timestamp (for sequentiality)

    The result is then base64 encoded.

    """
    _uuid = uuid4()
    _now = now()
    return urlsafe_b64encode(f"{_uuid}-{_now}".encode()).decode()
