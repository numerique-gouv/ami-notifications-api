from typing import Any

from litestar import Litestar
from litestar.testing import TestClient

from app.models import User

from .utils import check_url_when_logged_out


async def test_rvo_test_list_users_when_logged_in(
    test_client: TestClient[Litestar],
    userinfo: dict[str, Any],
    user: User,
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": userinfo})
    response = test_client.get("/rvo")
    assert response.status_code == 200
    assert "/rvo/test" in response.text

    response = test_client.get("/rvo/test")
    assert response.status_code == 200
    assert f"ID : {user.id}, email : {user.email}" in response.text


async def test_rvo_test_list_users_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out("/rvo/test", test_client)
