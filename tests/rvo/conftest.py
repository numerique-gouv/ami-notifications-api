from typing import Any, cast

import pytest

from app.models import User
from tests.base import ConnectedTestClient, TestClient


@pytest.fixture
async def connected_test_client(
    user: User,
    test_client: TestClient,
    userinfo: dict[str, Any],
) -> ConnectedTestClient:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": userinfo})
    test_client.user = user
    test_client.userinfo = userinfo
    return cast(ConnectedTestClient, test_client)
