import datetime
import uuid
from typing import Any

from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.types import DateTimeUTC, JsonB
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from webpush import WebPushSubscription

from app import schemas

Base = UUIDAuditBase


class Nonce(Base):
    __tablename__ = "nonce"

    nonce: Mapped[str] = mapped_column(String(256))


class User(Base):
    __tablename__ = "ami_user"  # type: ignore

    fc_hash: Mapped[str] = mapped_column(unique=True)
    last_logged_in: Mapped[datetime.datetime | None] = mapped_column(DateTimeUTC(timezone=True))

    registrations: Mapped[list["Registration"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    scheduled_notifications: Mapped[list["ScheduledNotification"]] = relationship(
        back_populates="user"
    )


class Registration(Base):
    __tablename__ = "registration"  # type: ignore

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="registrations")
    subscription: Mapped[dict[str, Any]] = mapped_column(JsonB, nullable=True)

    @property
    def typed_subscription(self) -> "WebPushSubscription | schemas.MobileAppSubscription":
        """Convert the stored dict to the proper subscription type."""
        from app import schemas

        try:
            return WebPushSubscription.model_validate(self.subscription)
        except Exception:
            return schemas.MobileAppSubscription.model_validate(self.subscription)


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

    try_push: Mapped[bool | None]
    send_status: Mapped[bool | None]

    read: Mapped[bool] = mapped_column(default=False)


class ScheduledNotification(Base):
    __tablename__ = "scheduled_notification"  # type: ignore

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ami_user.id"))
    user: Mapped[User] = relationship(back_populates="scheduled_notifications")

    content_title: Mapped[str]
    content_body: Mapped[str]
    content_icon: Mapped[str]

    sender: Mapped[str]

    reference: Mapped[str]
    scheduled_at: Mapped[datetime.datetime]
    sent_at: Mapped[datetime.datetime | None]

    __table_args__ = (UniqueConstraint("user_id", "reference", name="uix_user_reference"),)
