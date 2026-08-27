import datetime
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from itertools import chain

from ami.notification.models import Notification
from ami.partner.models import Partner
from ami.service.models import Service


class ItemGenericStatus(Enum):
    NEW = "new"
    WIP = "wip"
    CLOSED = "closed"


class FollowupSourceStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class FollowupItemEvent:
    id: str
    created_at: datetime.datetime
    description: str


@dataclass
class FollowupSubItem:
    partner_id: str
    item_type: str
    item_external_id: str
    reference: str
    status_id: ItemGenericStatus
    status_label: str
    milestone_start_date: datetime.datetime | None
    milestone_end_date: datetime.datetime | None

    events: list[FollowupItemEvent]

    title: str
    subheading: str
    description: str
    icon: str
    external_url: str | None
    is_archived: bool

    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class FollowupItem(FollowupSubItem):
    sub_items: list[FollowupSubItem]


@dataclass
class FollowupSource:
    status: FollowupSourceStatus = field(default=FollowupSourceStatus.LOADING)
    items: list[FollowupItem] = field(default_factory=list[FollowupItem])


@dataclass
class Followup:
    notifications: FollowupSource | None = field(default_factory=FollowupSource)


@dataclass
class NotificationsSubItem:
    notifications: list[Notification] = field(default_factory=list[Notification])
    services_by_id: dict[str, Service] = field(default_factory=dict[str, Service])
    partners_by_slug: dict[str, Partner] = field(default_factory=dict[str, Partner])

    followup_item_klass = FollowupSubItem

    @property
    def service(self):
        return self.services_by_id.get(f"{self.partner_id}:{self.item_type}")

    @property
    def first_notification(self):
        return self.notifications[0]

    @property
    def last_notification(self):
        return self.notifications[-1]

    @property
    def partner_id(self):
        return self.last_notification.partner.slug

    @property
    def partner(self):
        return self.partners_by_slug.get(self.partner_id)

    @property
    def item_type(self):
        return self.last_notification.item_type

    @property
    def item_external_id(self):
        return self.last_notification.item_id

    @property
    def reference(self):
        # sub item has no reference
        return ""

    @property
    def notification_for_status(self):
        # for a sub_item, take last notification status (more recent)
        return self.last_notification

    @property
    def status_id(self):
        # adapt status (typing)
        return ItemGenericStatus(self.notification_for_status.item_generic_status)

    @property
    def status_label(self):
        return self.notification_for_status.item_status_label or ""

    @property
    def milestone_start_date(self):
        return self.last_notification.item_milestone_start_date

    @property
    def milestone_end_date(self):
        return self.last_notification.item_milestone_end_date

    @property
    def events(self):
        events = []
        for notification in self.notifications:
            event_description = notification.content_body
            if notification.content_private_body:
                event_description += f"\n\n{notification.content_private_body}"
            events.append(
                FollowupItemEvent(notification.id, notification.created_at, event_description)
            )
        return events

    @property
    def title(self):
        # get sub item title from subheading and item_id
        return self.last_notification.content_subheading or self.last_notification.item_id

    @property
    def subheading(self) -> str:
        # sub item has no subheading
        return ""

    @property
    def description(self):
        description = self.last_notification.content_body
        if self.last_notification.content_private_body:
            description += f"\n\n{self.last_notification.content_private_body}"
        return description

    @property
    def icon(self):
        return self.last_notification.icon or ""

    @property
    def external_url(self):
        # sub item has no external_url
        return None

    @property
    def is_archived(self):
        # last non null is_archived seen
        is_archived_flags = [
            n.item_is_archived for n in self.notifications if n.item_is_archived is not None
        ]
        return is_archived_flags[-1] if is_archived_flags else False

    @property
    def created_at(self):
        return self.first_notification.event_date

    @property
    def updated_at(self):
        return self.last_notification.event_date

    def get_followup_item_kwargs(self):
        return {
            "partner_id": self.partner_id,
            "item_type": self.item_type,
            "item_external_id": self.item_external_id,
            "reference": self.reference,
            "status_id": self.status_id,
            "status_label": self.status_label,
            "milestone_start_date": self.milestone_start_date,
            "milestone_end_date": self.milestone_end_date,
            "events": self.events,
            "title": self.title,
            "subheading": self.subheading,
            "description": self.description,
            "icon": self.icon,
            "external_url": self.external_url,
            "is_archived": self.is_archived,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def build_followup_item(self) -> FollowupSubItem | None:
        try:
            return FollowupSubItem(
                **self.get_followup_item_kwargs(),
            )
        except ValueError:
            return None


@dataclass
class NotificationsItem(NotificationsSubItem):
    sub_items: dict[str, NotificationsSubItem] = field(
        default_factory=dict[str, NotificationsSubItem]
    )

    followup_item_klass = FollowupItem

    @property
    def followup_sub_items(self):
        # build sub_items
        sub_items = []
        for sub_item in self.sub_items.values():
            followup_sub_item = sub_item.build_followup_item()
            if followup_sub_item is None:
                continue
            sub_items.append(followup_sub_item)
        return sorted(sub_items, key=lambda a: (a.updated_at, a.created_at), reverse=True)

    def get_followup_item_kwargs(self):
        kwargs = super().get_followup_item_kwargs()
        kwargs["sub_items"] = self.followup_sub_items
        return kwargs

    def build_followup_item(self) -> FollowupItem | None:
        try:
            return FollowupItem(
                **self.get_followup_item_kwargs(),
            )
        except ValueError:
            return None

    @cached_property
    def sub_items_notifications(self):
        notifications = list(
            chain.from_iterable(sub_item.notifications for sub_item in self.sub_items.values())
        )
        return sorted(notifications, key=lambda a: (a.event_date, a.created_at))

    @cached_property
    def all_notifications(self):
        notifications = self.notifications + self.sub_items_notifications
        return sorted(notifications, key=lambda a: (a.event_date, a.created_at))

    @property
    def first_notification(self):
        if not self.notifications:
            return self.sub_items_notifications[0]
        return self.notifications[0]

    @property
    def last_notification(self):
        if not self.notifications:
            return self.sub_items_notifications[-1]
        return self.notifications[-1]

    @property
    def partner_id(self):
        if not self.notifications and self.sub_items:
            # take sub_item parent value
            return self.last_notification.item_parent_partner.slug
        return self.last_notification.partner.slug

    @property
    def item_type(self):
        if not self.notifications and self.sub_items:
            # take sub_item parent value
            return self.last_notification.item_parent_type
        return self.last_notification.item_type

    @property
    def item_external_id(self):
        if not self.notifications and self.sub_items:
            # take sub_item parent value
            return self.last_notification.item_parent_id
        return self.last_notification.item_id

    @property
    def reference(self):
        return self.item_external_id

    @property
    def notification_for_status(self):
        def is_last_notification_about_item():
            # return True if parent fields are empty
            if self.all_notifications[-1].item_parent_partner:
                return False
            if self.all_notifications[-1].item_parent_type:
                return False
            if self.all_notifications[-1].item_parent_id:
                return False
            return True

        if not self.sub_items:
            # return last notification
            return self.last_notification

        if is_last_notification_about_item():
            # return the last notification (from all notifications) if it is about item
            return self.all_notifications[-1]

        # return the last notification of sub_items by priority (new then wip then closed)
        status_priority = {
            ItemGenericStatus.NEW.value: 2,
            ItemGenericStatus.WIP.value: 1,
            ItemGenericStatus.CLOSED.value: 0,
        }
        last_sub_item_notifications = [
            sub_item.last_notification for sub_item in self.sub_items.values()
        ]
        last_sub_item_notifications = sorted(
            last_sub_item_notifications,
            key=lambda a: (status_priority[a.item_generic_status], a.event_date, a.created_at),
        )
        return last_sub_item_notifications[-1]

    @property
    def title(self):
        if self.service is not None:
            # take service name if exists
            return self.service.title
        if self.last_notification.content_title:
            return self.last_notification.content_title
        # last title seen
        titles = [n.content_title for n in self.all_notifications if n.content_title]
        return titles[-1] if titles else ""

    @property
    def subheading(self):
        if not self.notifications and self.sub_items:
            # take partner name if found, else item_parent_type
            if self.partner:
                return self.partner.name
            return self.item_type
        if self.last_notification.content_subheading:
            return self.last_notification.content_subheading
        if self.partner:
            return self.partner.name
        return ""

    @property
    def icon(self):
        return self.all_notifications[-1].icon or ""

    @property
    def external_url(self):
        # last external_url seen
        external_urls = [n.content_link for n in self.all_notifications if n.content_link]
        return external_urls[-1] if external_urls else None

    @property
    def created_at(self):
        return self.all_notifications[0].event_date

    @property
    def updated_at(self):
        return self.all_notifications[-1].event_date


@dataclass
class NotificationsFollowup:
    items: dict[str, NotificationsItem] = field(default_factory=dict[str, NotificationsItem])
    services_by_id: dict[str, Service] = field(default_factory=dict[str, Service])
    partners_by_slug: dict[str, Partner] = field(default_factory=dict[str, Partner])

    def add_notification(self, item_id, notification):
        if item_id not in self.items:
            self.items[item_id] = NotificationsItem(
                services_by_id=self.services_by_id, partners_by_slug=self.partners_by_slug
            )
        self.items[item_id].notifications.append(notification)

    def add_sub_notification(self, item_parent_id, item_id, notification):
        if item_parent_id not in self.items:
            self.items[item_parent_id] = NotificationsItem(
                services_by_id=self.services_by_id, partners_by_slug=self.partners_by_slug
            )
        if item_id not in self.items[item_parent_id].sub_items:
            self.items[item_parent_id].sub_items[item_id] = NotificationsSubItem()
        self.items[item_parent_id].sub_items[item_id].notifications.append(notification)

    def complete_notifications(self):
        for item in self.items.values():
            for item_id, sub_item in item.sub_items.items():
                if item_id in self.items:
                    # item is child and parent ...
                    self.items[item_id].notifications += sub_item.notifications

        # special case: no notifications for parent and only one sub_item: transform sub_item into item
        for item in self.items.values():
            if not item.notifications and len(item.sub_items.values()) == 1:
                item.notifications = list(item.sub_items.values())[0].notifications
                item.sub_items = {}

        # sort notifications
        for item in self.items.values():
            item.notifications = sorted(
                item.notifications, key=lambda a: (a.event_date, a.created_at)
            )
            for sub_item in item.sub_items.values():
                sub_item.notifications = sorted(
                    sub_item.notifications, key=lambda a: (a.event_date, a.created_at)
                )
