import datetime
from typing import Any

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from advanced_alchemy.types import JsonB
from litestar.exceptions import NotFoundException
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.base import ExecutableOption


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "ami_user"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    birthcountry: Mapped[int | None]
    birthdate: Mapped[datetime.date | None]
    birthplace: Mapped[int | None]
    email: Mapped[str | None]
    family_name: Mapped[str | None]
    gender: Mapped[str | None]
    given_name: Mapped[str | None]
    registrations: Mapped[list["Registration"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")

    @property
    def name(self):
        return f"{self.family_name} {self.given_name}"


class FCUserInfo(BaseModel):
    birthcountry: int | None
    birthdate: datetime.date | None = None
    birthplace: int | None = None
    email: str | None = None
    family_name: str | None = None
    gender: str | None = None
    given_name: str | None = None


class Registration(Base):
    __tablename__ = "registration"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="registrations")
    subscription: Mapped[dict[str, Any]] = mapped_column(JsonB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)


class RegistrationCreate(BaseModel):
    user_id: int
    subscription: dict[str, Any]


class RegistrationDTO(SQLAlchemyDTO[Registration]):
    config = SQLAlchemyDTOConfig(exclude={"user"})


class Notification(Base):
    __tablename__ = "notification"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="notifications")
    message: Mapped[str]
    sender: Mapped[str | None]
    title: Mapped[str | None]
    date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    unread: Mapped[bool] = mapped_column(default=True)


class NotificationCreate(BaseModel):
    user_id: int
    message: str = Field(min_length=1)
    sender: str | None
    title: str | None


class NotificationRead(BaseModel):
    read: bool


class NotificationDTO(SQLAlchemyDTO[Notification]):
    config = SQLAlchemyDTOConfig(exclude={"user"})


#### USERS


async def get_user_by_id(
    user_id: int, db_session: AsyncSession, options: ExecutableOption | None = None
) -> User:
    query = select(User).where(User.id == user_id)
    if options:
        query = query.options(options)
    result = await db_session.execute(query)
    try:
        return result.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User with id {user_id!r} not found") from e


async def get_user_by_userinfo(
    userinfo: FCUserInfo, db_session: AsyncSession, options: ExecutableOption | None = None
) -> User:
    constraints = [
        getattr(User, field) == value for (field, value) in userinfo.model_dump().items()
    ]
    query = select(User).where(*constraints)
    if options:
        query = query.options(options)
    result = await db_session.execute(query)
    try:
        return result.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User {userinfo.given_name!r} not found") from e


async def get_user_list(
    db_session: AsyncSession,
    options: ExecutableOption | None = None,
) -> list[User]:
    query = select(User)
    if options:
        query = query.options(options)
    query = query.order_by(User.id)
    result = await db_session.execute(query)
    return list(result.scalars().all())


async def create_user_from_userinfo(user: User, db_session: AsyncSession) -> User:
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


#### NOTIFICATIONS


async def get_notification_list_by_user(
    user: User, db_session: AsyncSession, unread: bool | None = None
) -> list[Notification]:
    query = select(Notification).where(Notification.user == user)
    if unread is not None:
        query = query.where(Notification.unread == unread)
    query = query.order_by(Notification.date.desc())
    result = await db_session.execute(query)
    return list(result.scalars().all())


async def create_notification(notification: Notification, db_session: AsyncSession) -> Notification:
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


async def get_notification_by_id_and_user(
    notification_id: int, user: User, db_session: AsyncSession
) -> Notification:
    query = select(Notification).where(
        Notification.id == notification_id, Notification.user == user
    )
    result = await db_session.execute(query)
    try:
        return result.scalar_one()
    except NoResultFound as e:
        raise NotFoundException(
            detail=f"Notification with id {notification_id!r} not found for the user"
        ) from e


async def update_notification(db_session: AsyncSession, notification: Notification) -> Notification:
    db_session.add(notification)
    await db_session.commit()
    await db_session.refresh(notification)
    return notification


#### REGISTRATIONS


async def get_registration_by_user_and_subscription(
    subscription: dict[str, Any], db_session: AsyncSession, user: User
) -> Registration | None:
    query = select(Registration).where(
        Registration.user == user, Registration.subscription == subscription
    )
    result = await db_session.execute(query)
    existing_registration = result.scalars().first()
    return existing_registration


async def create_registration(registration: Registration, db_session: AsyncSession) -> Registration:
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return registration
