from collections.abc import AsyncGenerator, Iterator
from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from webpush import WebPush
from webpush.vapid import VAPID

from app import create_app, session_config
from app.database import DATABASE_URL, alchemy_config
from app.models import Base, Notification, Registration, User

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
    app: Litestar,
    engine: AsyncEngine,
    sessionmaker: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(alchemy_config, "session_maker", sessionmaker)
    monkeypatch.setattr(alchemy_config, "engine_instance", engine)


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
def test_client(app: Litestar) -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app, session_config=session_config) as client:
        yield client


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    user_ = User(email="user@example.com", family_name="AMI", given_name="Test User")
    db_session.add(user_)
    await db_session.commit()
    return user_


@pytest.fixture
async def notification(db_session: AsyncSession, registration: Registration) -> Notification:
    notification_ = Notification(
        user_id=registration.user.id,
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()
    return notification_


@pytest.fixture
async def registration(
    db_session: AsyncSession, user: User, webpushsubscription: dict[str, Any]
) -> Registration:
    registration_ = Registration(user_id=user.id, subscription=webpushsubscription)
    db_session.add(registration_)
    await db_session.commit()
    return registration_


@pytest.fixture
async def webpushsubscription() -> dict[str, Any]:
    subscription = {
        "endpoint": "https://example.com",
        "keys": {
            "auth": "ribfIxhEOtCZ0lkcbB4yCg",
            "p256dh": "BGsTJAJDhGijvPLi0DVPHB86MGLmW1Y6VzjX-FpTlKbhhOtCmU0Vffaj1djCXzR6vkUYrwkOTmh1dgbIQHEyy1k",
        },
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
