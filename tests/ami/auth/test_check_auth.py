from litestar import Litestar
from litestar.testing import TestClient

from app.models import User
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_check_auth(
    user: User,
    test_client: TestClient[Litestar],
) -> None:
    login(user, test_client)
    response = test_client.get("/check-auth")
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


async def test_check_auth_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/check-auth", test_client)
