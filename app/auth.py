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
from app.services.user import UserService, provide_users_service


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
    users_service: UserService = await anext(
        provide_users_service(
            alchemy_config.provide_session(connection.app.state, connection.scope)
        )
    )
    user = await users_service.get_one_or_none(id=token.sub)
    return user


jwt_cookie_auth = JWTCookieAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=str(env.AUTH_COOKIE_JWT_SECRET),
    samesite="none",
    secure=True,
)

openapi_config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
)
