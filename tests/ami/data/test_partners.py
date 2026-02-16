import datetime
from unittest import mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.partners import get_partner_data, get_psl_inventory
from app.data.schemas import (
    FollowUpInventory,
    FollowUpInventoryItem,
    FollowUpInventoryItemKind,
    FollowUpInventoryStatus,
)
from app.models import Notification, User
from app.schemas import ItemGenericStatus
from app.services.notification import NotificationService


async def test_get_partner_data_no_notifications_for_user(
    user: User,
    db_session: AsyncSession,
    notifications_service: NotificationService,
) -> None:
    other_user = User(fc_hash="fc-hash")
    db_session.add(other_user)
    await db_session.commit()
    other_notification = Notification(
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(other_notification)
    await db_session.commit()

    result = await get_partner_data(
        current_user=user, partner_id="psl", notifications_service=notifications_service
    )

    assert result == []


async def test_get_partner_data_no_notifications_for_partner(
    user: User,
    db_session: AsyncSession,
    notifications_service: NotificationService,
) -> None:
    other_notification = Notification(
        user_id=user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="PSL",
        partner_id="other_partner",
    )
    db_session.add(other_notification)
    await db_session.commit()

    result = await get_partner_data(
        current_user=user, partner_id="psl", notifications_service=notifications_service
    )

    assert result == []


async def test_get_partner_data_incomplete_notifications(
    user: User,
    db_session: AsyncSession,
    notifications_service: NotificationService,
) -> None:
    # no item_generic_status
    notification1 = Notification(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification1)
    await db_session.commit()
    # no item_status_label
    notification1 = Notification(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification1)
    await db_session.commit()
    # no item_type
    notification1 = Notification(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification1)
    await db_session.commit()
    # no item_id
    notification1 = Notification(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification1)
    await db_session.commit()

    result = await get_partner_data(
        current_user=user, partner_id="psl", notifications_service=notifications_service
    )

    assert result == []


async def test_get_partner_data_invalid_notifications(
    user: User,
    db_session: AsyncSession,
    notifications_service: NotificationService,
) -> None:
    # invalid item_generic_status
    notification1 = Notification(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="invalid",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification1)
    await db_session.commit()

    result = await get_partner_data(
        current_user=user, partner_id="psl", notifications_service=notifications_service
    )

    assert result == []


async def test_get_partner_data(
    user: User,
    db_session: AsyncSession,
    notifications_service: NotificationService,
) -> None:
    notification1 = Notification(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification1)
    await db_session.commit()
    notification2 = Notification(
        user_id=user.id,
        content_body="notification 2",
        content_title="Notification title 2",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification2)
    await db_session.commit()
    notification3 = Notification(
        user_id=user.id,
        content_body="notification 3",
        content_title="Notification title 3",
        item_generic_status="wip",
        item_status_label="En cours",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification3)
    await db_session.commit()

    notification4 = Notification(
        user_id=user.id,
        content_body="notification 4",
        content_title="Notification title 4",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="43",
        item_external_url="http://foo.com",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification4)
    await db_session.commit()

    notification5 = Notification(
        user_id=user.id,
        content_body="notification 5",
        content_title="Notification title 5",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="44",
        item_external_url="http://bar.com",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification5)
    await db_session.commit()
    notification6 = Notification(
        user_id=user.id,
        content_body="notification 6",
        content_title="Notification title 6",
        item_generic_status="closed",
        item_status_label="Validé",
        item_type="OperationTranquilliteVacances",
        item_id="44",
        item_milestone_start_date=datetime.datetime.now(datetime.timezone.utc),
        item_milestone_end_date=datetime.datetime.now(datetime.timezone.utc),
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(notification6)
    await db_session.commit()

    other_notification = Notification(
        user_id=user.id,
        content_body="other notification",
        content_title="Other Notification title",
        item_type="unknown",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    db_session.add(other_notification)
    await db_session.commit()

    result = await get_partner_data(
        current_user=user, partner_id="psl", notifications_service=notifications_service
    )

    assert result == [
        FollowUpInventoryItem(
            external_id="OperationTranquilliteVacances:44",
            kind=FollowUpInventoryItemKind.OTV,
            status_id=ItemGenericStatus.CLOSED,
            status_label="Validé",
            milestone_start_date=notification6.item_milestone_start_date,
            milestone_end_date=notification6.item_milestone_end_date,
            title="Notification title 6",
            description="notification 6",
            external_url="http://bar.com",
            created_at=notification5.send_date,
            updated_at=notification6.send_date,
        ),
        FollowUpInventoryItem(
            external_id="OperationTranquilliteVacances:43",
            kind=FollowUpInventoryItemKind.OTV,
            status_id=ItemGenericStatus.NEW,
            status_label="Nouveau",
            milestone_start_date=None,
            milestone_end_date=None,
            title="Notification title 4",
            description="notification 4",
            external_url="http://foo.com",
            created_at=notification4.send_date,
            updated_at=notification4.send_date,
        ),
        FollowUpInventoryItem(
            external_id="OperationTranquilliteVacances:42",
            kind=FollowUpInventoryItemKind.OTV,
            status_id=ItemGenericStatus.WIP,
            status_label="En cours",
            milestone_start_date=None,
            milestone_end_date=None,
            title="Notification title 3",
            description="notification 3",
            external_url=None,
            created_at=notification1.send_date,
            updated_at=notification3.send_date,
        ),
    ]


async def test_get_psl_inventory(
    user: User,
    notifications_service: NotificationService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    items = [
        FollowUpInventoryItem(
            external_id="OperationTranquilliteVacances:44",
            kind=FollowUpInventoryItemKind.OTV,
            status_id=ItemGenericStatus.CLOSED,
            status_label="Validé",
            milestone_start_date=datetime.datetime.now(datetime.timezone.utc),
            milestone_end_date=datetime.datetime.now(datetime.timezone.utc),
            title="Notification title 6",
            description="notification 6",
            external_url="http://bar.com",
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
        FollowUpInventoryItem(
            external_id="OperationTranquilliteVacances:43",
            kind=FollowUpInventoryItemKind.OTV,
            status_id=ItemGenericStatus.NEW,
            status_label="Nouveau",
            milestone_start_date=None,
            milestone_end_date=None,
            title="Notification title 4",
            description="notification 4",
            external_url="http://foo.com",
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    ]
    data_mock = mock.AsyncMock(return_value=items)
    monkeypatch.setattr("app.data.partners.get_partner_data", data_mock)
    result = await get_psl_inventory(current_user=user, notifications_service=notifications_service)
    assert result == FollowUpInventory(status=FollowUpInventoryStatus.SUCCESS, items=items)
