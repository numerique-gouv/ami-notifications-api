import datetime
from base64 import urlsafe_b64encode
from typing import Any
from uuid import uuid4

from litestar.connection import ASGIConnection
from litestar.openapi.config import OpenAPIConfig
from litestar.security.jwt import JWTCookieAuth, Token

from app import env
from app.database import alchemy_config
from app.models import User
from app.services.revoked_auth_token import RevokedAuthTokenService
from app.services.user import UserService


def generate_nonce() -> str:
    """Generate a NONCE by concatenating:
    - a uuid4 (for randomness and high confidence of uniqueness)
    - the curent timestamp (for sequentiality)

    The result is then base64 encoded.

    """
    uuid = uuid4()
    now: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
    return urlsafe_b64encode(f"{uuid}-{now}".encode("utf8")).decode("utf8")


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    # Use async context manager to ensure session is properly closed
    async with alchemy_config.provide_session(connection.app.state, connection.scope) as session:
        users_service = UserService(session=session)
        user = await users_service.get_one_or_none(id=token.sub)

        # Expunge user from session so it can be used after session closes
        if user:
            session.expunge(user)

        return user


async def revoked_token_handler(
    token: Token, connection: "ASGIConnection[Any, Any, Any, Any]"
) -> bool:
    jti = token.jti  # Unique token identifier (JWT ID)
    if jti:
        # Use async context manager to ensure session is properly closed
        async with alchemy_config.provide_session(
            connection.app.state, connection.scope
        ) as session:
            revoked_auth_tokens_service = RevokedAuthTokenService(session=session)
            revoked = await revoked_auth_tokens_service.get_one_or_none(jti=jti)
            if revoked:
                return True
    return False


jwt_cookie_auth = JWTCookieAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    revoked_token_handler=revoked_token_handler,
    token_secret=str(env.AUTH_COOKIE_JWT_SECRET),
    default_token_expiration=datetime.timedelta(days=365 * 10),  # 10 years
    samesite="none",
    secure=True,
)


openapi_config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
)
