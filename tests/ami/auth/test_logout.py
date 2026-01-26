from litestar import Litestar
from litestar.testing import TestClient

from app.auth import jwt_cookie_auth
from app.models import User
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_logout(
    user: User,
    test_client: TestClient[Litestar],
) -> None:
    login(user, test_client)
    assert test_client.cookies.get(jwt_cookie_auth.key)
    response = test_client.post("/logout")
    assert response.status_code == 201
    assert not response.cookies.get(jwt_cookie_auth.key)


async def test_logout_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/logout", test_client, method="post")
