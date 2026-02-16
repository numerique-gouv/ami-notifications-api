import collections

from app.data.schemas import (
    FollowUpInventory,
    FollowUpInventoryItem,
    FollowUpInventoryItemKind,
    FollowUpInventoryStatus,
)
from app.models import Notification, User
from app.schemas import ItemGenericStatus
from app.services.notification import NotificationService


async def get_psl_inventory(
    *,
    current_user: User,
    notifications_service: NotificationService,
) -> FollowUpInventory:
    inventory = FollowUpInventory()

    notifications: list[Notification] = list(
        await notifications_service.list(
            order_by=(Notification.send_date, False),
            user=current_user,
            partner_id="psl",
        )
    )

    notifications_by_item_ids: collections.defaultdict[str, list[Notification]] = (
        collections.defaultdict(list)
    )
    for notification in notifications:
        external_id = f"{notification.item_type}:{notification.item_id}"
        notifications_by_item_ids[external_id].append(notification)

    for external_id, notifications in notifications_by_item_ids.items():
        first_notification = notifications[0]
        last_notification = notifications[-1]
        inventory.items.append(
            FollowUpInventoryItem(
                external_id=f"{last_notification.item_type}:{last_notification.item_id}",
                kind=FollowUpInventoryItemKind.OTV,
                status_id=ItemGenericStatus(last_notification.item_generic_status),
                status_label=last_notification.item_status_label or "",
                milestone_start_date=last_notification.item_milestone_start_date,
                milestone_end_date=last_notification.item_milestone_end_date,
                title="Opération Tranquillité Vacances",
                description="Pendant toute absence prolongée de votre résidence principale, "
                "les services de police ou de gendarmerie se chargeront de surveiller gratuitement votre domicile.",
                created_at=first_notification.send_date,
                updated_at=last_notification.send_date,
            )
        )

    inventory.status = FollowUpInventoryStatus.SUCCESS
    return inventory
