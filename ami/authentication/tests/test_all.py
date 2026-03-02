import datetime
from base64 import urlsafe_b64encode

import pytest

from ami.authentication.utils import generate_nonce


def test_generate_nonce(monkeypatch: pytest.MonkeyPatch) -> None:
    FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)
    FAKE_UUID = "fake-uuid"

    monkeypatch.setattr("ami.authentication.utils.uuid4", lambda: FAKE_UUID)
    monkeypatch.setattr("ami.authentication.utils.now", lambda: FAKE_TIME)
    assert generate_nonce() == urlsafe_b64encode(f"{FAKE_UUID}-{FAKE_TIME}".encode("utf8")).decode(
        "utf8"
    )
