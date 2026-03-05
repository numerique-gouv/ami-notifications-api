import asyncio
import uuid

from litestar import Litestar
from litestar.channels import Subscriber
from litestar.security.jwt import Token
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import jwt_cookie_auth
from app.models import RevokedAuthToken, User


def login(user: User, test_client: TestClient[Litestar]) -> None:
    response = jwt_cookie_auth.login(
        identifier=str(user.id),
        token_unique_jwt_id=uuid.uuid4().hex,
    )
    test_client.cookies.update({jwt_cookie_auth.key: str(response.cookies[0].value)})


def get_token(encoded: str) -> Token:
    return Token.decode(
        encoded_token=encoded,
        secret=jwt_cookie_auth.token_secret,
        algorithm=jwt_cookie_auth.algorithm,
    )


async def assert_query_fails_without_auth(
    tested_url: str,
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    method: str = "get",
) -> None:
    response = getattr(test_client, method)(tested_url)
    assert response.status_code == 401

    test_client.cookies.update({jwt_cookie_auth.key: "Bearer: bad-value"})
    response = getattr(test_client, method)(tested_url)
    assert response.status_code == 401

    user = User(fc_hash="foo")
    db_session.add(user)
    await db_session.commit()
    login(user, test_client)
    token = get_token(test_client.cookies[jwt_cookie_auth.key].split(" ")[1])
    revoked = RevokedAuthToken(jti=token.jti)
    db_session.add(revoked)
    await db_session.commit()
    response = getattr(test_client, method)(tested_url)
    assert response.status_code == 401


# TODO: remove when all the litestar tests using it have been migrated to Django
async def get_from_stream(subscriber: Subscriber, count: int) -> list[bytes]:
    async def getter() -> list[bytes]:
        items: list[bytes] = []
        async for item in subscriber.iter_events():
            items.append(item)
            if len(items) == count:
                break
        return items

    return await asyncio.wait_for(getter(), timeout=1)
