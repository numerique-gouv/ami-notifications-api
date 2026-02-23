from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import jwt_cookie_auth
from app.models import RevokedAuthToken, User
from tests.ami.utils import assert_query_fails_without_auth, get_token, login


async def test_logout(
    user: User,
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
) -> None:
    login(user, test_client)
    token = get_token(test_client.cookies[jwt_cookie_auth.key].split(" ")[1])
    assert test_client.cookies.get(jwt_cookie_auth.key)
    response = test_client.post("/logout")
    assert response.status_code == 201
    assert not response.cookies.get(jwt_cookie_auth.key)
    all_revoked_auth_tokens = (await db_session.execute(select(RevokedAuthToken))).scalars().all()
    assert len(all_revoked_auth_tokens) == 1
    revoked_auth_token = all_revoked_auth_tokens[0]
    assert revoked_auth_token.jti == token.jti


async def test_logout_without_auth(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
) -> None:
    await assert_query_fails_without_auth("/logout", test_client, db_session, method="post")
