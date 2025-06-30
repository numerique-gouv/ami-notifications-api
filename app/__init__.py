import json
import os
import uuid
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from pathlib import Path
from typing import Annotated, Any, Callable, cast

import httpx
import sentry_sdk
from litestar import Litestar, Response, get, post
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Body
from litestar.response import Template
from litestar.static_files import (
    create_static_files_router,  # type: ignore[reportUnknownVariableType]
)
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from litestar.template.config import TemplateConfig
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import InstrumentedAttribute, selectinload
from sqlalchemy.sql.base import ExecutableOption
from sqlmodel import Column, Field, Relationship, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush, WebPushSubscription

from .database import db_connection, provide_db_session

cors_config = CORSConfig(allow_origins=["*"])


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),
    environment=os.getenv("SENTRY_ENV", ""),
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # send_default_pii=True,
)

# This is the folder where the svelte PWA is built statically.
HTML_DIR = "public/mobile-app/build"

# This is the folder where the "admin" (test API client) is.
HTML_DIR_ADMIN = "public"


#### MODELS


class User(SQLModel, table=True):
    __tablename__ = "ami_user"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    email: str
    registrations: list["Registration"] = Relationship(back_populates="user")
    notifications: list["Notification"] = Relationship(back_populates="user")


class Registration(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="ami_user.id")
    user: User = Relationship(back_populates="registrations")
    subscription: dict[str, Any] = Field(sa_column=Column(JSONB))
    label: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)


class RegistrationCreation(SQLModel, table=False):
    subscription: dict[str, Any] = Field(sa_column=Column(JSONB))
    email: str


class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="ami_user.id")
    user: User = Relationship(back_populates="notifications")
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
        RegistrationCreation,
        Body(
            title="Register to receive notifications",
            description="Register with a push subscription and an email to receive notifications",
        ),
    ],
) -> Response[Registration]:
    WebPushSubscription.model_validate(data.subscription)
    try:
        user = await get_user_by_email(data.email, db_session)
    except NotFoundException:
        user = User(email=data.email)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    assert user.id is not None, "User ID should be set after commit"
    query = select(Registration).where(
        col(Registration.user) == user, col(Registration.subscription) == data.subscription
    )
    result = await db_session.exec(query)
    existing_registration = result.first()
    if existing_registration:
        # This registration already exists, don't duplicate it.
        return Response(existing_registration, status_code=HTTP_200_OK)

    registration = Registration(subscription=data.subscription, user_id=user.id)
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return Response(registration, status_code=HTTP_201_CREATED)


async def get_user_by_email(
    email: str, db_session: AsyncSession, options: ExecutableOption | None = None
) -> User:
    if options:
        query = select(User).where(col(User.email) == email).options(options)
    else:
        query = select(User).where(col(User.email) == email)
    result = await db_session.exec(query)
    try:
        return result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User {email!r} not found") from e


async def get_user_by_id(
    user_id: int, db_session: AsyncSession, options: ExecutableOption | None = None
) -> User:
    if options:
        query = select(User).where(col(User.id) == user_id).options(options)
    else:
        query = select(User).where(col(User.id) == user_id)
    result = await db_session.exec(query)
    try:
        return result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User with id {user_id!r} not found") from e


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
    user = await get_user_by_id(
        data.user_id,
        db_session,
        options=selectinload(cast(InstrumentedAttribute[Any], User.registrations)),
    )

    for registration in user.registrations:
        subscription = WebPushSubscription.model_validate(registration.subscription)
        json_data = {"title": data.title, "message": data.message, "sender": data.sender}
        message = webpush.get(message=json.dumps(json_data), subscription=subscription)
        headers = cast(dict[str, str], message.headers)

        response = httpx.post(
            registration.subscription["endpoint"], content=message.encrypted, headers=headers
        )
        response.raise_for_status()
    db_session.add(data)
    await db_session.commit()
    await db_session.refresh(data)
    return data


async def get_user_list(
    db_session: AsyncSession,
    options: ExecutableOption | None = None,
) -> list[User]:
    if options:
        query = select(User).options(options)
    else:
        query = select(User)
    query = query.order_by(col(User.id))
    result = await db_session.exec(query)
    return list(result.all())


async def get_registration_list(
    db_session: AsyncSession,
    options: ExecutableOption | None = None,
) -> list[Registration]:
    if options:
        query = select(Registration).options(options)
    else:
        query = select(Registration)
    query = query.order_by(col(Registration.user_id))
    result = await db_session.exec(query)
    return list(result.all())


async def get_notification_list(db_session: AsyncSession) -> list[Notification]:
    query = select(Notification).order_by(col(Notification.date).desc())
    result = await db_session.exec(query)
    return list(result.all())


@get("/notification/users")
async def list_users(db_session: AsyncSession) -> list[Registration]:
    # TODO: this should instead return a list of users, and thus use `get_user_list`.
    return await get_registration_list(db_session)


@get("/notifications/{email:str}")
async def get_notifications(db_session: AsyncSession, email: str) -> list[Notification]:
    user: User = await get_user_by_email(
        email,
        db_session,
        options=selectinload(cast(InstrumentedAttribute[Any], User.notifications)),
    )
    return user.notifications


#### VIEWS


@get(path="/admin/", include_in_schema=False)
async def admin(db_session: AsyncSession) -> Template:
    users = await get_user_list(db_session)
    notifications = await get_notification_list(db_session)
    return Template(
        template_name="admin.html",
        context={"users": users, "notifications": notifications},
    )


#### APP


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=os.getenv("VAPID_PUBLIC_KEY", "").encode(),
        private_key=os.getenv("VAPID_PRIVATE_KEY", "").encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush


def create_app(
    database_connection: Callable[[Litestar], AbstractAsyncContextManager[None]] = db_connection,
    webpush_init: Callable[[], WebPush] = provide_webpush,
) -> Litestar:
    return Litestar(
        route_handlers=[
            get_application_key,
            register,
            notify,
            list_users,
            get_notifications,
            admin,
            create_static_files_router(
                path="/admin/static",
                directories=[HTML_DIR_ADMIN],
                html_mode=True,
            ),
            create_static_files_router(
                path="/",
                directories=[HTML_DIR],
                html_mode=True,
            ),
        ],
        dependencies={
            "db_session": Provide(provide_db_session),
            "webpush": Provide(webpush_init, use_cache=True, sync_to_thread=True),
        },
        lifespan=[database_connection],
        template_config=TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine),
        cors_config=cors_config,
    )
