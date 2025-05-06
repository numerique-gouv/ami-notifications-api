import os
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, cast

import requests
from litestar import Litestar, get, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Body
from litestar.static_files import create_static_files_router
from sqlalchemy.exc import NoResultFound
from sqlalchemy.types import JSON
from sqlmodel import Column, Field, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush, WebPushSubscription

from .database import db_connection, provide_db_session

wp = WebPush(
    public_key=Path("./public_key.pem"),
    private_key=os.getenv("VAPID_PRIVATE_KEY", "").encode(),
    subscriber="mathieu@agopian.info",
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
    db_session: AsyncSession,
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
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return registration


async def get_user_by_email(email: str, db_session: AsyncSession) -> Registration:
    query = select(Registration).where(col(Registration.email) == email)
    result = await db_session.exec(query)
    try:
        return result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User {email!r} not found") from e


@post("/notification/send")
async def notify(
    db_session: AsyncSession,
    data: Annotated[
        Notification,
        Body(
            title="Send a notification",
            description="Send the notification message to a registered user",
        ),
    ],
) -> Notification:
    registration = await get_user_by_email(data.email, db_session)

    subscription = WebPushSubscription.model_validate(registration.subscription)
    message = wp.get(message=data.message, subscription=subscription)
    headers = cast(dict, message.headers)

    response = requests.post(
        registration.subscription["endpoint"], data=message.encrypted, headers=headers
    )
    if response.ok:
        db_session.add(data)
        await db_session.commit()
        await db_session.refresh(data)
    return data


async def get_user_list(db_session: AsyncSession) -> list[Registration]:
    query = select(Registration)
    result = await db_session.exec(query)
    return list(result.all())


@get("/notification/users")
async def list_users(db_session: AsyncSession) -> list[Registration]:
    return await get_user_list(db_session)


@get("/notifications/{email:str}")
async def get_notifications(db_session: AsyncSession, email: str) -> list[Notification]:
    query = select(Notification).where(col(Notification.email) == email)
    result = await db_session.exec(query)
    return list(result.all())


#### APP


def create_app(database_connection=db_connection) -> Litestar:
    return Litestar(
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
        dependencies={"db_session": Provide(provide_db_session)},
        lifespan=[database_connection],
    )
