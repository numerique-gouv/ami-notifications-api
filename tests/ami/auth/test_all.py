import datetime
from base64 import urlsafe_b64encode

import pytest

from app.auth import generate_nonce


async def test_generate_nonce(monkeypatch: pytest.MonkeyPatch) -> None:
    FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)
    FAKE_UUID = "fake-uuid"

    class mock_datetime(datetime.datetime):
        @classmethod
        def now(cls, tz: datetime.tzinfo | None = datetime.timezone.utc):
            return FAKE_TIME

    monkeypatch.setattr("app.auth.uuid4", lambda: FAKE_UUID)
    monkeypatch.setattr("app.auth.datetime.datetime", mock_datetime)
    assert generate_nonce() == urlsafe_b64encode(f"{FAKE_UUID}-{FAKE_TIME}".encode("utf8")).decode(
        "utf8"
    )
