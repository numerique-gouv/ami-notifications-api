import os
from collections.abc import Iterator

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app import Notification, app

app.debug = True


@pytest.fixture
def test_client(session: AsyncSession) -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as client:
        yield client


@pytest.fixture(name="session", scope="function")
async def session_fixture():
    engine = create_async_engine(os.getenv("DATABASE_URL", ""))
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def notification1(session: AsyncSession) -> Notification:
    notification_1 = Notification(email="foo@example.com", message="Hello notification 1")
    session.add(notification_1)
    await session.commit()
    return notification_1
