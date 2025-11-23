from litestar import Litestar
from litestar.testing import TestClient

from app.auth import jwt_cookie_auth
from app.models import User


def login(user: User, test_client: TestClient[Litestar]) -> None:
    response = jwt_cookie_auth.login(identifier=str(user.id))
    test_client.cookies.update({jwt_cookie_auth.key: str(response.cookies[0].value)})


async def assert_query_fails_without_auth(
    tested_url: str,
    test_client: TestClient[Litestar],
    method: str = "get",
) -> None:
    response = getattr(test_client, method)(tested_url)
    assert response.status_code == 401

    test_client.cookies.update({jwt_cookie_auth.key: "Bearer: bad-value"})
    response = getattr(test_client, method)(tested_url)
    assert response.status_code == 401
