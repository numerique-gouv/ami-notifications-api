import datetime
import secrets
from base64 import b64decode, urlsafe_b64encode
from typing import Any, Dict, Generic
from uuid import uuid4

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
    DefineMiddleware,
)
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.spec import Components, SecurityRequirement, SecurityScheme
from litestar.security.base import AbstractSecurityConfig, UserType
from litestar.security.jwt import JWTCookieAuth, Token
from typing_extensions import TypeVar

from app import env
from app.database import alchemy_config
from app.models import User
from app.partners import Partner, partners
from app.services.user import UserService, provide_users_service

PartnerT = TypeVar("PartnerT", bound=Partner, default=Partner)


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
    default_token_expiration=datetime.timedelta(days=365 * 10),  # 10 years
    samesite="none",
    secure=True,
)


class PartnerAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    async def authenticate_request(
        self, connection: ASGIConnection[Any, Any, Any, Any]
    ) -> AuthenticationResult:
        auth = connection.headers.get("authorization", "")
        if not auth:
            raise NotAuthorizedException()

        try:
            scheme, b64 = auth.split(" ", 1)
        except ValueError:
            raise NotAuthorizedException()

        if scheme.lower() != "basic":
            raise NotAuthorizedException()

        try:
            decoded = b64decode(b64, validate=True).decode("utf-8")
            partner_id, partner_secret = decoded.split(":", 1)
        except Exception:
            raise NotAuthorizedException()

        partner: Partner | None = partners.get(partner_id)
        if partner is None:
            raise NotAuthorizedException()

        if not secrets.compare_digest(partner.secret, partner_secret):
            raise NotAuthorizedException()

        return AuthenticationResult(user=partner, auth="basic")


class PartnerAuth(Generic[UserType, PartnerT], AbstractSecurityConfig[UserType, Dict[str, Any]]):
    @property
    def middleware(self) -> DefineMiddleware:
        return DefineMiddleware(PartnerAuthenticationMiddleware)

    @property
    def openapi_components(self) -> Components:
        return Components(
            security_schemes={
                "BasicAuth": SecurityScheme(
                    type="http",
                    scheme="Basic",
                    name="authorization",
                    security_scheme_in="header",
                    bearer_format="base64",
                )
            }
        )

    @property
    def security_requirement(self) -> SecurityRequirement:
        return {"BasicAuth": []}


partner_auth = PartnerAuth[Partner]()


openapi_config = OpenAPIConfig(
    title="My API",
    version="1.0.0",
    components=[jwt_cookie_auth.openapi_components, partner_auth.openapi_components],
    security=[jwt_cookie_auth.security_requirement, partner_auth.security_requirement],
)
