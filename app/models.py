import datetime
import uuid
from typing import Any

from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.types import DateTimeUTC, JsonB
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = UUIDAuditBase


class Nonce(Base):
    __tablename__ = "nonce"

    nonce: Mapped[str] = mapped_column(String(256))


class User(Base):
    __tablename__ = "ami_user"  # type: ignore

    fc_hash: Mapped[str] = mapped_column(unique=True)
    already_seen: Mapped[bool] = mapped_column(default=True)

    registrations: Mapped[list["Registration"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")


class Registration(Base):
    __tablename__ = "registration"  # type: ignore

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="registrations")
    subscription: Mapped[dict[str, Any]] = mapped_column(JsonB, nullable=True)


class Notification(Base):
    __tablename__ = "notification"  # type: ignore

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="notifications")

    content_title: Mapped[str]
    content_body: Mapped[str]
    content_icon: Mapped[str | None]

    sender: Mapped[str]

    item_type: Mapped[str | None]
    item_id: Mapped[str | None]
    item_status_label: Mapped[str | None]
    item_generic_status: Mapped[str | None]
    item_canal: Mapped[str | None]
    item_milestone_start_date: Mapped[datetime.datetime | None]
    item_milestone_end_date: Mapped[datetime.datetime | None]
    item_external_url: Mapped[str | None]

    send_date: Mapped[datetime.datetime] = mapped_column(
        DateTimeUTC(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    )

    unread: Mapped[bool] = mapped_column(default=True)
