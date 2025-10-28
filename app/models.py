import datetime
from typing import Any

from advanced_alchemy.base import DefaultBase
from advanced_alchemy.types import DateTimeUTC, JsonB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
