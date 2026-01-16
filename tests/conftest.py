import base64
import datetime
import importlib
import os
import time
from collections.abc import AsyncGenerator, Iterator
from typing import Any, cast

import litestar.cli.main
import pytest
from advanced_alchemy.extensions.litestar.providers import create_service_provider
from click.testing import CliRunner
from litestar import Litestar
from litestar.channels import ChannelsPlugin, Subscriber
from litestar.cli._utils import LitestarExtensionGroup
from litestar.middleware.session.server_side import ServerSideSessionConfig
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from webpush.vapid import VAPID

from app import create_app, env
from app.database import DATABASE_URL, alchemy_config
from app.models import Base, Notification, Registration, User
from app.services.notification import NotificationService
from app.services.scheduled_notification import ScheduledNotificationService
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
    monkeypatch.setattr("app.channels_dsn", TEST_DATABASE_URL.replace("+asyncpg", ""))


@pytest.fixture(autouse=True)
def patch_webpush(monkeypatch: pytest.MonkeyPatch) -> None:
    private_key, public_key, _ = VAPID.generate_keys()
    monkeypatch.setattr("app.webpush.env.VAPID_PRIVATE_KEY", private_key.decode())
    monkeypatch.setattr("app.webpush.env.VAPID_PUBLIC_KEY", public_key.decode())


@pytest.fixture
async def app() -> Litestar:
    app_ = create_app()
    app_.debug = True
    return app_


@pytest.fixture
def test_client(app: Litestar) -> Iterator[TestClient]:
    os.environ["TZ"] = "Europe/Paris"
    time.tzset()
    with TestClient(app=app, session_config=session_config) as client:
        yield client


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture()
def root_command() -> LitestarExtensionGroup:
    return cast("LitestarExtensionGroup", importlib.reload(litestar.cli.main).litestar_group)


@pytest.fixture
async def channels(app: Litestar) -> ChannelsPlugin:
    return app.plugins.get(ChannelsPlugin)


@pytest.fixture
async def notification_events_subscriber(channels: ChannelsPlugin) -> Subscriber:
    return await channels.subscribe("notification_events")


@pytest.fixture
async def scheduled_notifications_service(
    db_session: AsyncSession,
) -> ScheduledNotificationService:
    provide_scheduled_notifications_service = create_service_provider(ScheduledNotificationService)
    scheduled_notifications_service: ScheduledNotificationService = await anext(
        provide_scheduled_notifications_service(db_session)
    )
    return scheduled_notifications_service


@pytest.fixture
async def notifications_service(
    db_session: AsyncSession,
) -> NotificationService:
    provide_notifications_service = create_service_provider(NotificationService)
    notifications_service: NotificationService = await anext(
        provide_notifications_service(db_session)
    )
    return notifications_service


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
    user_ = User(fc_hash=fc_hash, last_logged_in=datetime.datetime.now(datetime.timezone.utc))
    db_session.add(user_)
    await db_session.commit()
    return user_


@pytest.fixture
async def never_seen_user(user: User, db_session: AsyncSession) -> User:
    user.last_logged_in = None
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def notification(db_session: AsyncSession, user: User) -> Notification:
    notification_ = Notification(
        user_id=user.id,
        content_body="Hello notification",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()
    return notification_


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
async def decoded_id_token() -> dict[str, Any]:
    return {
        "sub": "cff67ebe00792a2f2b5115dcc1a65d115adb3b73653fb3ed1b88ea11a7a2589av1",
        "auth_time": 1763455959,
        "acr": "eidas1",
        "nonce": "YTc3NzZlNjUtNmY3OC00YzExLThmODItMTg0MDg2ZjQ0YzEyLTIwMjUtMTEtMTggMDg6NTI6MzUuNjM1OTYyKzAwOjAw",
        "aud": "33fe498cc172fe691778912a2967baa650b24f1ae0ebbe47ae552f37b2d25ead",
        "exp": 1763456019,
        "iat": 1763455959,
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }


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
