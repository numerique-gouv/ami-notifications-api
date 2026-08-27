import collections

from ami.followup.schemas import (
    FollowupItem,
    FollowupSource,
    FollowupSourceStatus,
    NotificationsFollowup,
)
from ami.notification.models import Notification
from ami.partner.models import Partner
from ami.service.models import Service
from ami.user.models import User


def get_notifications_data(*, current_user: User) -> list[FollowupItem]:
    notifications = Notification.objects.filter(
        item_generic_status__isnull=False,
        item_status_label__isnull=False,
        item_type__isnull=False,
        item_id__isnull=False,
        user=current_user,
    ).select_related("partner", "item_parent_partner")

    services_by_id: collections.defaultdict[str, Service] = collections.defaultdict()
    for service in Service.objects.all().select_related("partner"):
        external_id = f"{service.partner.slug}:{service.item_type}"
        services_by_id[external_id] = service
    partners_by_slug = {p.slug: p for p in Partner.objects.all()}

    notifications_followup = NotificationsFollowup()
    notifications_followup.services_by_id = services_by_id
    notifications_followup.partners_by_slug = partners_by_slug
    for notification in notifications:
        external_id = f"{notification.partner.slug}:{notification.item_type}:{notification.item_id}"
        if (
            notification.item_parent_partner
            and notification.item_parent_type
            and notification.item_parent_id
        ):
            external_parent_id = f"{notification.item_parent_partner.slug}:{notification.item_parent_type}:{notification.item_parent_id}"
            notifications_followup.add_sub_notification(
                external_parent_id, external_id, notification
            )
        else:
            notifications_followup.add_notification(external_id, notification)

    notifications_followup.complete_notifications()

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
