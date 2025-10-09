from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient

from app.models import User


@pytest.fixture
async def connected_user(
    user: User,
    test_client: TestClient[Litestar],
    userinfo: dict[str, Any],
) -> User:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": userinfo})
    return user
