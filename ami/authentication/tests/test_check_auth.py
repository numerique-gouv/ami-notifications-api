import uuid

import pytest

from ami.authentication.auth import create_jwt_token
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_check_auth(
    app,
    user: User,
) -> None:
    login(app, user)
    response = app.get("/check-auth")
    assert response.status_code == 200
    assert response.json == {"authenticated": True}


@pytest.mark.django_db
def test_check_auth_with_headers(
    app,
    user: User,
) -> None:
    jwt_token = create_jwt_token(user_id=str(user.id), jti=uuid.uuid4().hex)
    response = app.get("/check-auth", headers={"Authorization": f"Bearer {jwt_token}"})
    assert response.status_code == 200
    assert response.json == {"authenticated": True}


@pytest.mark.django_db
def test_check_auth_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(app, "/check-auth")
