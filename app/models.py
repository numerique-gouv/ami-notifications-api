import datetime
import uuid
from typing import Any

from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.types import JsonB
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = UUIDAuditBase


class Nonce(Base):
    __tablename__ = "nonce"

    nonce: Mapped[str] = mapped_column(String(256))


class User(Base):
    __tablename__ = "ami_user"  # type: ignore

    fc_hash: Mapped[str | None]
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

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="registrations")
    subscription: Mapped[dict[str, Any]] = mapped_column(JsonB, nullable=True)


class Notification(Base):
    __tablename__ = "notification"  # type: ignore

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="notifications")
    message: Mapped[str]
    sender: Mapped[str | None]
    title: Mapped[str | None]
    unread: Mapped[bool] = mapped_column(default=True)
