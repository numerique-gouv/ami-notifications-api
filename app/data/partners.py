import collections

from app.data.schemas import (
    FollowUpInventory,
    FollowUpInventoryItem,
    FollowUpInventoryStatus,
)
from app.models import Notification, User
from app.services.notification import NotificationService


async def get_partner_data(
    *,
    current_user: User,
    partner_id: str,
    notifications_service: NotificationService,
) -> list[FollowUpInventoryItem]:
    notifications: list[Notification] = list(
        await notifications_service.list(
            Notification.item_generic_status.is_not(None),
            Notification.item_status_label.is_not(None),
            Notification.item_type.is_not(None),
            Notification.item_id.is_not(None),
            order_by=[(Notification.send_date, False), (Notification.created_at, False)],
            user=current_user,
            partner_id=partner_id,
        )
    )

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


async def get_partner_inventory(
    *,
    current_user: User,
    partner_id: str,
    notifications_service: NotificationService,
) -> FollowUpInventory:
    inventory = FollowUpInventory()

    items = await get_partner_data(
        current_user=current_user,
        partner_id=partner_id,
        notifications_service=notifications_service,
    )

    inventory.items = items
    inventory.status = FollowUpInventoryStatus.SUCCESS

    return inventory


async def get_psl_inventory(
    *,
    current_user: User,
    notifications_service: NotificationService,
) -> FollowUpInventory:
    inventory = await get_partner_inventory(
        current_user=current_user, partner_id="psl", notifications_service=notifications_service
    )
    return inventory
