import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Self

from ami.notification.models import Notification
from ami.utils.schemas import ExpirationRule, ItemGenericStatus


class AgendaCatalogStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


class AgendaCatalogItemKind(Enum):
    HOLIDAY = "holiday"
    ELECTION = "election"


@dataclass
class AgendaCatalogItem:
    kind: AgendaCatalogItemKind
    title: str
    description: str = field(default="")
    date: datetime.date | None = field(default=None)
    start_date: datetime.date | None = field(default=None)
    end_date: datetime.date | None = field(default=None)
    zones: str = field(default="")
    emoji: str = field(default="")


@dataclass
class AgendaCatalog:
    status: AgendaCatalogStatus = field(default=AgendaCatalogStatus.LOADING)
    items: list[AgendaCatalogItem] = field(default_factory=list[AgendaCatalogItem])
    expires_at: datetime.datetime | None = field(default=None)

    def set_expires_at(self, expiration_rule: ExpirationRule):
        self.expires_at = expiration_rule.compute_expires_at()


@dataclass
class Agenda:
    school_holidays: AgendaCatalog | None = field(default_factory=AgendaCatalog)
    public_holidays: AgendaCatalog | None = field(default_factory=AgendaCatalog)
    elections: AgendaCatalog | None = field(default_factory=AgendaCatalog)


class FollowUpInventoryStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


class FollowUpInventoryItemKind(Enum):
    OTV = "otv"


@dataclass
class FollowUpInventoryItem:
    external_id: str
    kind: FollowUpInventoryItemKind
    status_id: ItemGenericStatus
    status_label: str
    milestone_start_date: datetime.datetime | None
    milestone_end_date: datetime.datetime | None

    title: str
    description: str
    external_url: str | None

    created_at: datetime.datetime
    updated_at: datetime.datetime

    kind_mapping = {
        ("psl", "OperationTranquilliteVacances"): FollowUpInventoryItemKind.OTV,
    }

    @classmethod
    def from_notifications(cls, notifications: list[Notification]) -> Self | None:
        first_notification = notifications[0]
        last_notification = notifications[-1]
        external_urls = [n.item_external_url for n in notifications if n.item_external_url]
        assert last_notification.partner_id
        assert last_notification.item_type
        kind = cls.kind_mapping.get((last_notification.partner_id, last_notification.item_type))
        if kind is None:
            return None
        try:
            status_id = ItemGenericStatus(last_notification.item_generic_status)
        except ValueError:
            return None
        return cls(
            external_id=f"{last_notification.item_type}:{last_notification.item_id}",
            kind=kind,
            status_id=status_id,
            status_label=last_notification.item_status_label or "",
            milestone_start_date=last_notification.item_milestone_start_date,
            milestone_end_date=last_notification.item_milestone_end_date,
            title=last_notification.content_title,
            description=last_notification.content_body,
            external_url=external_urls[-1] if external_urls else None,
            created_at=first_notification.send_date,
            updated_at=last_notification.send_date,
        )


@dataclass
class FollowUpInventory:
    status: FollowUpInventoryStatus = field(default=FollowUpInventoryStatus.LOADING)
    items: list[FollowUpInventoryItem] = field(default_factory=list[FollowUpInventoryItem])


@dataclass
class FollowUp:
    psl: FollowUpInventory | None = field(default_factory=FollowUpInventory)
