import pytest

from ami.authentication.auth import decode_jwt_token
from ami.authentication.models import RevokedAuthToken
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_logout(
    settings,
    app,
    user: User,
) -> None:
    login(app, user)
    token = decode_jwt_token(
        app.cookies[settings.AUTH_COOKIE_JWT_NAME].split(" ")[1].replace('"', "")
    )
    assert token
    response = app.post("/logout")
    assert response.status_code == 201
    assert not response.client.cookies.get(settings.AUTH_COOKIE_JWT_NAME)
    assert not response.client.cookies.get(settings.USERINFO_COOKIE_JWT_NAME)
    assert RevokedAuthToken.objects.count() == 1
    revoked_auth_token = RevokedAuthToken.objects.get()
    assert revoked_auth_token.jti == token["jti"]


@pytest.mark.django_db
def test_logout_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(app, "/logout", method="post")
