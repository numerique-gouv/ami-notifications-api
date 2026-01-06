import datetime
import json
from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import jwt_cookie_auth
from app.models import ScheduledNotification, User
from app.utils import build_fc_hash


async def test_fc_get_userinfo(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    fake_userinfo_token = "fake userinfo jwt token"
    auth = {"authorization": "Bearer foobar_access_token"}
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
        is_reusable=True,
    )

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
        "user_first_login": True,
        "user_fc_hash": "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
    }

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1
    scheduled_notification = all_scheduled_notifications[0]
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "Bienvenue sur AMI 👋"
    assert (
        scheduled_notification.content_body
        == "Recevez des rappels sur votre situation et suivez vos démarches en cours depuis l'application."
    )
    assert scheduled_notification.content_icon == "fr-icon-information-line"
    assert scheduled_notification.reference == "ami:welcome"
    assert scheduled_notification.scheduled_at < datetime.datetime.now(datetime.timezone.utc)
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
        "user_first_login": False,
        "user_fc_hash": "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
    }
    assert "authorization" in response.headers
    assert "set-cookie" in response.headers
    assert response.cookies.get(jwt_cookie_auth.key)

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1


async def test_fc_get_userinfo_user_never_seen(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    fake_userinfo_token = "fake userinfo jwt token"
    auth = {"authorization": "Bearer foobar_access_token"}
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
        is_reusable=True,
    )

    fc_hash = build_fc_hash(
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
        birthdate=userinfo["birthdate"],
        gender=userinfo["gender"],
        birthplace=userinfo["birthplace"],
        birthcountry=userinfo["birthcountry"],
    )
    user = User(fc_hash=fc_hash)
    db_session.add(user)
    await db_session.commit()

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    assert all_users[0].id == user.id
    await db_session.refresh(user)
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
        "user_first_login": True,
        "user_fc_hash": "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
    }

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1
    scheduled_notification = all_scheduled_notifications[0]
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "Bienvenue sur AMI 👋"
    assert (
        scheduled_notification.content_body
        == "Recevez des rappels sur votre situation et suivez vos démarches en cours depuis l'application."
    )
    assert scheduled_notification.content_icon == "fr-icon-information-line"
    assert scheduled_notification.reference == "ami:welcome"
    assert scheduled_notification.scheduled_at < datetime.datetime.now(datetime.timezone.utc)
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None

    # again, if notification reference already exists
    user.last_logged_in = None
    db_session.add(user)
    await db_session.commit()
    response = test_client.get("/fc_userinfo", headers=auth)
    assert response.status_code == 200
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
        "user_first_login": True,
        "user_fc_hash": "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
    }
    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1
