import base64
import os
import time
from collections.abc import AsyncGenerator, Iterator
from typing import Any

import pytest
from litestar import Litestar
from litestar.middleware.session.server_side import ServerSideSessionConfig
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from webpush import WebPush
from webpush.vapid import VAPID

from app import create_app, env
from app.database import DATABASE_URL, alchemy_config
from app.models import Base, Notification, Registration, User
from app.utils import build_fc_hash
from tests.base import TestClient

session_config = ServerSideSessionConfig()

TEST_DATABASE_URL = f"{DATABASE_URL}_test"


@pytest.fixture
async def engine() -> AsyncEngine:
    return create_async_engine(
        TEST_DATABASE_URL,
        # avoid event loop issues
        poolclass=NullPool,
    )


@pytest.fixture
async def sessionmaker(
    engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    yield async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
async def db_session(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as _session:
        yield _session


@pytest.fixture(autouse=True)
async def seed_db(
    engine: AsyncEngine,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(autouse=True)
def patch_db(
    sessionmaker: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(alchemy_config, "session_maker", sessionmaker)


def test_webpush() -> WebPush:
    private_key, public_key, _ = VAPID.generate_keys()
    return WebPush(
        private_key=private_key,
        public_key=public_key,
        subscriber="administrator@example.com",
    )


@pytest.fixture
async def app() -> Litestar:
    app_ = create_app(webpush_init=test_webpush)
    app_.debug = True
    return app_


@pytest.fixture
def test_client(app: Litestar) -> Iterator[TestClient]:
    os.environ["TZ"] = "Europe/Paris"
    time.tzset()
    with TestClient(app=app, session_config=session_config) as client:
        yield client


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    fc_hash = build_fc_hash(
        given_name="Test User",
        family_name="AMI",
        birthdate="",
        gender="",
        birthplace="",
        birthcountry="",
    )
    user_ = User(fc_hash=fc_hash)
    db_session.add(user_)
    await db_session.commit()
    return user_


@pytest.fixture
async def never_seen_user(user: User, db_session: AsyncSession) -> User:
    user.already_seen = False
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def webpush_notification(
    db_session: AsyncSession, webpush_registration: Registration
) -> Notification:
    notification_ = Notification(
        user_id=webpush_registration.user.id,
        content_body="Hello notification",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()
    return notification_


@pytest.fixture
async def webpush_registration(
    db_session: AsyncSession, user: User, webpushsubscription: dict[str, Any]
) -> Registration:
    registration_ = Registration(user_id=user.id, subscription=webpushsubscription)
    db_session.add(registration_)
    await db_session.commit()
    return registration_


@pytest.fixture
async def webpushsubscription() -> dict[str, Any]:
    subscription = {
        "endpoint": "https://example.com/",
        "keys": {
            "auth": "ribfIxhEOtCZ0lkcbB4yCg",
            "p256dh": "BGsTJAJDhGijvPLi0DVPHB86MGLmW1Y6VzjX-FpTlKbhhOtCmU0Vffaj1djCXzR6vkUYrwkOTmh1dgbIQHEyy1k",
        },
    }
    return subscription


@pytest.fixture
async def mobile_notification(
    db_session: AsyncSession, mobile_registration: Registration
) -> Notification:
    notification_ = Notification(
        user_id=mobile_registration.user.id,
        content_body="Hello notification",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()
    return notification_


@pytest.fixture
async def mobile_registration(
    db_session: AsyncSession, user: User, mobileAppSubscription: dict[str, Any]
) -> Registration:
    registration_ = Registration(user_id=user.id, subscription=mobileAppSubscription)
    db_session.add(registration_)
    await db_session.commit()
    return registration_


@pytest.fixture
async def mobileAppSubscription() -> dict[str, Any]:
    subscription = {
        "app_version": "0.0-local",
        "device_id": "some-id",
        "fcm_token": "some-token",
        "model": "Google sdk_gphone64_arm64",
        "platform": "android",
    }
    return subscription


@pytest.fixture
async def userinfo() -> dict[str, Any]:
    return {
        "sub": "fake sub",
        "given_name": "Angela Claire Louise",
        "given_name_array": ["Angela", "Claire", "Louise"],
        "family_name": "DUBOIS",
        "birthdate": "1962-08-24",
        "birthcountry": "99100",
        "birthplace": "75107",
        "gender": "female",
        "email": "angela@dubois.fr",
        "aud": "fake aud",
        "exp": 1753877658,
        "iat": 1753877598,
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }


@pytest.fixture
async def jwt_encoded_userinfo() -> str:
    return '"eyJhbGciOiJFUzI1NiIsImtpZCI6InBrY3MxMTpFUzI1Njpoc20ifQ.eyJzdWIiOiI0Y2U0ZjBjY2Y1Nzc1NjAyYTUyNGIzZjA2OTY2ODM0NTlhOTgwMmQyYmM0NGEzNDI2M2M4ZTMzZmRhZjUxNTM2djEiLCJnaXZlbl9uYW1lIjoiQW5nZWxhIENsYWlyZSBMb3Vpc2UiLCJnaXZlbl9uYW1lX2FycmF5IjpbIkFuZ2VsYSIsIkNsYWlyZSIsIkxvdWlzZSJdLCJmYW1pbHlfbmFtZSI6IkRVQk9JUyIsImJpcnRoZGF0ZSI6IjE5NjItMDgtMjQiLCJnZW5kZXIiOiJmZW1hbGUiLCJiaXJ0aHBsYWNlIjoiNzUxMDciLCJiaXJ0aGNvdW50cnkiOiI5OTEwMCIsImVtYWlsIjoid29zc2V3b2RkYS0zNzI4QHlvcG1haWwuY29tIiwiYXVkIjoiZmI5NjE1Mjk0Yzc0NjE0NWVkZDg1N2I0ZWRiZWI0OTk2ZTMxNmFlMTcxMmVkMmJiMzYxMTUwYTFlNmNkOGM2ZiIsImV4cCI6MTc2MzQ3NDgyMiwiaWF0IjoxNzYzNDc0NzYyLCJpc3MiOiJodHRwczovL2ZjcC1sb3cuc2J4LmRldi1mcmFuY2Vjb25uZWN0LmZyL2FwaS92MiJ9.c-pqPyDy4UZTR4gq8Bh93hdKkY_iUREHfptt-0X-L5-ABQnYOblfNMjvUFLvTVltbOy-KJh85DOHpTVdrX7j1Q"'


@pytest.fixture
async def partner_auth() -> dict[str, str]:
    b64 = base64.b64encode(f"psl:{env.PARTNERS_PSL_SECRET}".encode("utf8")).decode("utf8")
    return {"authorization": f"Basic {b64}"}
