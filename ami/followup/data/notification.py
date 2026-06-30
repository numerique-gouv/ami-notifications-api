import collections

from ami.followup.schemas import FollowupItem, FollowupSource, FollowupSourceStatus
from ami.notification.models import Notification
from ami.partner.models import partners
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

    notifications_by_item_ids: collections.defaultdict[str, list[Notification]] = (
        collections.defaultdict(list)
    )
    for notification in notifications:
        external_id = f"{notification.partner_id}:{notification.item_type}:{notification.item_id}"
        notifications_by_item_ids[external_id].append(notification)

    items: list[FollowupItem] = []

    for notifications in notifications_by_item_ids.values():
        item = FollowupItem.from_notifications(notifications)
        if item is None:
            continue
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
