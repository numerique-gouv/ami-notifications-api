import collections

from ami.followup.schemas import (
    FollowupItem,
    FollowupSource,
    FollowupSourceStatus,
    NotificationsFollowup,
)
from ami.notification.models import Notification
from ami.partner.models import partners
from ami.service.models import Service
from ami.user.models import User


def get_notifications_data(*, current_user: User) -> list[FollowupItem]:
    notifications = Notification.objects.filter(
        item_generic_status__isnull=False,
        item_status_label__isnull=False,
        item_type__isnull=False,
        item_id__isnull=False,
        user=current_user,
        partner_id__in=[p.id for p in partners.values() if p.followup_from_notifications],
    ).order_by("event_date", "created_at")

    services_by_id: collections.defaultdict[str, Service] = collections.defaultdict()
    for service in Service.objects.all():
        external_id = f"{service.partner_id}:{service.item_type}"
        services_by_id[external_id] = service

    notifications_followup = NotificationsFollowup()
    notifications_followup.services_by_id = services_by_id
    for notification in notifications:
        external_id = f"{notification.partner_id}:{notification.item_type}:{notification.item_id}"
        if (
            notification.item_parent_partner_id
            and notification.item_parent_type
            and notification.item_parent_id
        ):
            external_parent_id = f"{notification.item_parent_partner_id}:{notification.item_parent_type}:{notification.item_parent_id}"
            notifications_followup.add_sub_notification(
                external_parent_id, external_id, notification
            )
        else:
            notifications_followup.add_notification(external_id, notification)

    items: list[FollowupItem] = []

    for notifications_item in notifications_followup.items.values():
        item = notifications_item.build_followup_item()
        if item is None:
            continue
        assert isinstance(item, FollowupItem)  # should not happen
        items.append(item)

    return sorted(items, key=lambda a: (a.updated_at, a.created_at), reverse=True)


def get_notifications_source(
    *,
    current_user: User,
) -> FollowupSource:
    source = FollowupSource()

    items = get_notifications_data(current_user=current_user)

    source.items = items
    source.status = FollowupSourceStatus.SUCCESS

    return source
