import urllib.parse
import uuid

from django.conf import settings

from ami.authentication.auth import create_jwt_token, decode_jwt_token
from ami.authentication.models import RevokedAuthToken
from ami.user.models import User


def url_contains_param(param_name: str, param_value: str, url: str) -> bool:
    url_encoded_value = urllib.parse.quote_plus(param_value)
    return f"{param_name}={url_encoded_value}" in url


def login(django_app, user: User) -> None:
    jwt_token = create_jwt_token(user_id=str(user.id), jti=uuid.uuid4().hex)
    django_app.set_cookie(settings.AUTH_COOKIE_JWT_NAME, f"Bearer {jwt_token}")


def assert_query_fails_without_auth(
    django_app,
    tested_url: str,
    method: str = "get",
) -> None:
    getattr(django_app, method)(tested_url, status=401)

    django_app.set_cookie(settings.AUTH_COOKIE_JWT_NAME, "Bearer bad-value")
    getattr(django_app, method)(tested_url, status=401)

    user = User.objects.create(fc_hash="foo")
    login(django_app, user)
    token = decode_jwt_token(
        django_app.cookies[settings.AUTH_COOKIE_JWT_NAME].split(" ")[1].replace('"', "")
    )
    assert token
    RevokedAuthToken.objects.create(jti=token["jti"])
    getattr(django_app, method)(tested_url, status=401)
