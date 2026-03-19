import collections

from ami.followup.schemas import FollowUpInventory, FollowUpInventoryItem, FollowUpInventoryStatus
from ami.notification.models import Notification
from ami.user.models import User


def get_partner_data(
    *,
    current_user: User,
    partner_id: str,
) -> list[FollowUpInventoryItem]:
    notifications = Notification.objects.filter(
        item_generic_status__isnull=False,
        item_status_label__isnull=False,
        item_type__isnull=False,
        item_id__isnull=False,
        user=current_user,
        partner_id=partner_id,
    ).order_by("send_date", "created_at")

    notifications_by_item_ids: collections.defaultdict[str, list[Notification]] = (
        collections.defaultdict(list)
    )
    for notification in notifications:
        external_id = f"{notification.item_type}:{notification.item_id}"
        notifications_by_item_ids[external_id].append(notification)

    items: list[FollowUpInventoryItem] = []

    for notifications in notifications_by_item_ids.values():
        item = FollowUpInventoryItem.from_notifications(notifications)
        if item is None:
            continue
        items.append(item)

    return sorted(items, key=lambda a: (a.updated_at, a.created_at), reverse=True)


def get_partner_inventory(
    *,
    current_user: User,
    partner_id: str,
) -> FollowUpInventory:
    inventory = FollowUpInventory()

    items = get_partner_data(
        current_user=current_user,
        partner_id=partner_id,
    )

    inventory.items = items
    inventory.status = FollowUpInventoryStatus.SUCCESS

    return inventory


def get_psl_inventory(
    *,
    current_user: User,
) -> FollowUpInventory:
    inventory = get_partner_inventory(current_user=current_user, partner_id="psl")
    return inventory
