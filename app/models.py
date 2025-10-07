import datetime
from typing import Any

from litestar.exceptions import NotFoundException
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.base import ExecutableOption
from sqlmodel import Column, Field, Relationship, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession


class FCUserInfo(SQLModel, table=False):
    birthcountry: int | None = Field(default=None)
    birthdate: datetime.date | None = Field(default=None)
    birthplace: int | None = Field(default=None)
    email: str | None = Field(default=None)
    family_name: str | None = Field(default=None)
    gender: str | None = Field(default=None)
    given_name: str | None = Field(default=None)

    @property
    def name(self):
        return f"{self.family_name} {self.given_name}"


class User(FCUserInfo, table=True):
    __tablename__ = "ami_user"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    registrations: Mapped[list["Registration"]] = Relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = Relationship(back_populates="user")


class Registration(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="ami_user.id")
    user: User = Relationship(back_populates="registrations")
    subscription: dict[str, Any] = Field(sa_column=Column(JSONB))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime.datetime = Field(default_factory=datetime.datetime.now)
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


async def get_user_by_userinfo(
    userinfo: FCUserInfo, db_session: AsyncSession, options: ExecutableOption | None = None
) -> User:
    constraints = [col(getattr(User, field)) == value for (field, value) in vars(userinfo).items()]
    query = select(User).where(*constraints)
    if options:
        query = query.options(options)
    result = await db_session.exec(query)
    try:
        return result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User {userinfo.given_name!r} not found") from e


async def get_user_list(
    db_session: AsyncSession,
    options: ExecutableOption | None = None,
) -> list[User]:
    query = select(User)
    if options:
        query = query.options(options)
    query = query.order_by(col(User.id))
    result = await db_session.exec(query)
    return list(result.all())


async def create_user_from_userinfo(user: User, db_session: AsyncSession) -> User:
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
    db_session: AsyncSession,
    user_id: int,
) -> Registration:
    registration = Registration(subscription=subscription, user_id=user_id)
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return registration
