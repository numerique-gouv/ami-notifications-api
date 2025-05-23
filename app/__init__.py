import json
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, cast

import httpx
from litestar import Litestar, get, post
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Body
from litestar.response import Template
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from sqlalchemy.exc import NoResultFound
from sqlalchemy.types import JSON
from sqlmodel import Column, Field, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush, WebPushSubscription

from .database import db_connection, provide_db_session

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
    sender: str | None = Field(default=None)
    title: str | None = Field(default=None)


#### ENDPOINTS


@get("/notification/key")
async def get_application_key() -> str:
    return os.getenv("VAPID_APPLICATION_SERVER_KEY", "")


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
    webpush: WebPush,
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
    json_data = {"title": data.title, "message": data.message, "sender": data.sender}
    message = webpush.get(message=json.dumps(json_data), subscription=subscription)
    headers = cast(dict, message.headers)

    response = httpx.post(
        registration.subscription["endpoint"], content=message.encrypted, headers=headers
    )
    response.raise_for_status()
    db_session.add(data)
    await db_session.commit()
    await db_session.refresh(data)
    return data


async def get_registration_list(db_session: AsyncSession) -> list[Registration]:
    query = select(Registration).order_by(col(Registration.email).desc())
    result = await db_session.exec(query)
    return list(result.all())


async def get_notification_list(db_session: AsyncSession) -> list[Notification]:
    query = select(Notification).order_by(col(Notification.date).desc())
    result = await db_session.exec(query)
    return list(result.all())


@get("/notification/users")
async def list_users(db_session: AsyncSession) -> list[Registration]:
    return await get_registration_list(db_session)


@get("/notifications/{email:str}")
async def get_notifications(db_session: AsyncSession, email: str) -> list[Notification]:
    query = select(Notification).where(col(Notification.email) == email)
    result = await db_session.exec(query)
    return list(result.all())


#### VIEWS


@get(path="/admin/", sync_to_thread=False)
async def admin(db_session: AsyncSession) -> Template:
    registrations = await get_registration_list(db_session)
    notifications = await get_notification_list(db_session)
    return Template(
        template_name="admin.html",
        context={"registrations": registrations, "notifications": notifications},
    )


#### APP


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=os.getenv("VAPID_PUBLIC_KEY", "").encode(),
        private_key=os.getenv("VAPID_PRIVATE_KEY", "").encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush


def create_app(database_connection=db_connection, webpush_init=provide_webpush) -> Litestar:
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
            admin,
        ],
        dependencies={
            "db_session": Provide(provide_db_session),
            "webpush": Provide(webpush_init, use_cache=True, sync_to_thread=True),
        },
        lifespan=[database_connection],
        template_config=TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine),
    )
