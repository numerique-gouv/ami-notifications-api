import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Self

from ami.notification.models import Notification


class ItemGenericStatus(Enum):
    NEW = "new"
    WIP = "wip"
    CLOSED = "closed"


class FollowupSourceStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class FollowupItem:
    partner_id: str
    item_type: str
    item_external_id: str
    status_id: ItemGenericStatus
    status_label: str
    milestone_start_date: datetime.datetime | None
    milestone_end_date: datetime.datetime | None

    title: str
    description: str
    icon: str
    external_url: str | None
    is_archived: bool

    created_at: datetime.datetime
    updated_at: datetime.datetime

    @classmethod
    def from_notifications(cls, notifications: list[Notification]) -> Self | None:
        first_notification = notifications[0]
        last_notification = notifications[-1]
        external_urls = [n.content_link for n in notifications if n.content_link]
        is_archived_flags = [
            n.item_is_archived for n in notifications if n.item_is_archived is not None
        ]
        description = last_notification.content_body
        if last_notification.content_private_body:
            description += f"\n\n{last_notification.content_private_body}"
        try:
            status_id = ItemGenericStatus(last_notification.item_generic_status)
        except ValueError:
            return None
        return cls(
            partner_id=last_notification.partner_id,
            item_type=last_notification.item_type,
            item_external_id=last_notification.item_id,
            status_id=status_id,
            status_label=last_notification.item_status_label or "",
            milestone_start_date=last_notification.item_milestone_start_date,
            milestone_end_date=last_notification.item_milestone_end_date,
            title=last_notification.content_title,
            description=description,
            icon=last_notification.icon or "",
            # last external_url seen
            external_url=external_urls[-1] if external_urls else None,
            # last non null is_archived seen
            is_archived=is_archived_flags[-1] if is_archived_flags else False,
            created_at=first_notification.event_date,
            updated_at=last_notification.event_date,
        )


@dataclass
class FollowupSource:
    status: FollowupSourceStatus = field(default=FollowupSourceStatus.LOADING)
    items: list[FollowupItem] = field(default_factory=list[FollowupItem])


@dataclass
class Followup:
    notifications: FollowupSource | None = field(default_factory=FollowupSource)
