import datetime
from typing import Any

from advanced_alchemy.base import DefaultBase
from advanced_alchemy.types import DateTimeUTC, JsonB
from litestar.exceptions import NotFoundException
from sqlalchemy import ForeignKey, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.base import ExecutableOption

Base = DefaultBase


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


class Registration(Base):
    __tablename__ = "registration"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="registrations")
    subscription: Mapped[dict[str, Any]] = mapped_column(JsonB, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )


class Notification(Base):
    __tablename__ = "notification"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="notifications")
    message: Mapped[str]
    sender: Mapped[str | None]
    title: Mapped[str | None]
    date: Mapped[datetime.datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )
    unread: Mapped[bool] = mapped_column(default=True)


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
