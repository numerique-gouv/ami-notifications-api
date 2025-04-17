import os
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, cast

import requests
from litestar import Litestar, get, post
from litestar.di import Provide
from litestar.exceptions import ClientException, NotFoundException
from litestar.params import Body
from litestar.static_files import create_static_files_router
from litestar.status_codes import HTTP_409_CONFLICT
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.types import JSON
from sqlmodel import Column, Field, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush, WebPushSubscription

wp = WebPush(
    public_key=Path("./public_key.pem"),
    private_key=os.getenv("VAPID_PRIVATE_KEY", "").encode(),
    subscriber="mathieu@agopian.info",
)

DATABASE_URL_RAW = os.getenv("DATABASE_URL", "")
# If we get a url with extra options like ?sslmode=prefer or not using the
# propper protocol `postgresql+asyncpg`, fix it.
DATABASE_URL = DATABASE_URL_RAW.replace("postgresql://", "postgresql+asyncpg://").replace(
    "?sslmode=prefer", ""
)
HTML_DIR = "public"


#### MODELS


class Registration(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str
    subscription: dict[str, Any] = Field(sa_column=Column(JSON), default={"all": "true"})


class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now)
    email: str
    message: str


#### ENDPOINTS


@get("/notification/key")
async def get_application_key() -> str:
    with open("applicationServerKey", "r") as applicationServerKey:
        return applicationServerKey.read()


@post("/notification/register")
async def register(
    session: AsyncSession,
    data: Annotated[
        Registration,
        Body(
            title="Register to receive notifications",
            description="Register with a push subscription and an email to receive notifications",
        ),
    ],
) -> Registration:
    WebPushSubscription.model_validate(data.subscription)
    registration = data
    session.add(registration)
    await session.commit()
    await session.refresh(registration)
    return registration


async def get_user_by_email(email: str, session: AsyncSession) -> Registration:
    query = select(Registration).where(col(Registration.email) == email)
    result = await session.exec(query)
    try:
        return result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User {email!r} not found") from e


@post("/notification/send")
async def notify(
    session: AsyncSession,
    data: Annotated[
        Notification,
        Body(
            title="Send a notification",
            description="Send the notification message to a registered user",
        ),
    ],
) -> Notification:
    registration = await get_user_by_email(data.email, session)

    subscription = WebPushSubscription.model_validate(registration.subscription)
    message = wp.get(message=data.message, subscription=subscription)
    headers = cast(dict, message.headers)

    response = requests.post(
        registration.subscription["endpoint"], data=message.encrypted, headers=headers
    )
    if response.ok:
        session.add(data)
        await session.commit()
        await session.refresh(data)
    return data


async def get_user_list(session: AsyncSession) -> list[Registration]:
    query = select(Registration)
    result = await session.exec(query)
    return list(result.all())


@get("/notification/users")
async def list_users(session: AsyncSession) -> list[Registration]:
    return await get_user_list(session)


@get("/notifications/{email:str}")
async def get_notifications(session: AsyncSession, email: str) -> list[Notification]:
    query = select(Notification).where(col(Notification.email) == email)
    result = await session.exec(query)
    return list(result.all())


#### DATABASE

engine = create_async_engine(DATABASE_URL, echo=True)


async def session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with AsyncSession(engine) as session:
            yield session

    except IntegrityError as exc:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


async def create_all_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


#### APP

app = Litestar(
    route_handlers=[
        create_static_files_router(
            path="/",
            directories=[HTML_DIR],
            html_mode=True,
        ),
        get_application_key,
        register,
        notify,
        list_users,
        get_notifications,
    ],
    dependencies={"session": Provide(session)},
    on_startup=[create_all_db_and_tables],
)
