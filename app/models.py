import uuid
from datetime import datetime
from typing import Any

from litestar.exceptions import NotFoundException
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.base import ExecutableOption
from sqlmodel import Column, Field, Relationship, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession


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
    label: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enabled: bool = Field(default=True)


class RegistrationRename(SQLModel, table=False):
    label: str


class RegistrationEnable(SQLModel, table=False):
    enabled: bool


class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="ami_user.id")
    user: User = Relationship(back_populates="notifications")
    message: str
    sender: str | None = Field(default=None)
    title: str | None = Field(default=None)


#### USERS


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


async def create_user(email: str, db_session: AsyncSession) -> User:
    user = User(email=email)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


#### NOTIFICATIONS


async def get_notification_list(db_session: AsyncSession) -> list[Notification]:
    query = select(Notification).order_by(col(Notification.date).desc())
    result = await db_session.exec(query)
    return list(result.all())


async def create_notification(notification: Notification, db_session: AsyncSession) -> Notification:
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


#### REGISTRATIONS


async def get_registration_by_id(db_session: AsyncSession, pk: int) -> Registration:
    query = select(Registration).where(col(Registration.id) == pk)
    result = await db_session.exec(query)
    try:
        registration: Registration = result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"Registration {pk!r} not found") from e
    return registration


async def get_registration_by_user_and_subscription(
    subscription: dict[str, Any], db_session: AsyncSession, user: User
) -> Registration | None:
    query = select(Registration).where(
        col(Registration.user) == user, col(Registration.subscription) == subscription
    )
    result = await db_session.exec(query)
    existing_registration = result.first()
    return existing_registration


async def create_registration(
    subscription: dict[str, Any],
    label: str,
    enabled: bool,
    db_session: AsyncSession,
    user_id: int,
) -> Registration:
    registration = Registration(
        subscription=subscription, label=label, enabled=enabled, user_id=user_id
    )
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return registration


async def update_registration(db_session: AsyncSession, registration: Registration) -> Registration:
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return registration
