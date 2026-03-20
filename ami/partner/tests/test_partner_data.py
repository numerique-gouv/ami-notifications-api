import datetime
from unittest import mock

import pytest

from ami.followup.schemas import (
    FollowUpInventory,
    FollowUpInventoryItem,
    FollowUpInventoryItemKind,
    FollowUpInventoryStatus,
)
from ami.notification.models import Notification
from ami.partner.models import get_partner_data, get_psl_inventory
from ami.user.models import User
from ami.utils.schemas import ItemGenericStatus


@pytest.mark.django_db
def test_get_partner_data_no_notifications_for_user(user: User) -> None:
    other_user = User.objects.create(fc_hash="fc-hash")
    Notification.objects.create(  # Other notification
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="PSL",
        partner_id="psl",
    )

    result = get_partner_data(current_user=user, partner_id="psl")

    assert result == []


@pytest.mark.django_db
def test_get_partner_data_no_notifications_for_partner(user: User) -> None:
    Notification.objects.create(  # Other notification
        user_id=user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="PSL",
        partner_id="other_partner",
    )

    result = get_partner_data(current_user=user, partner_id="psl")

    assert result == []


@pytest.mark.django_db
def test_get_partner_data_incomplete_notifications(user: User) -> None:
    # no item_generic_status
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    # no item_status_label
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    # no item_type
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )
    # no item_id
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        sender="PSL",
        partner_id="psl",
    )

    result = get_partner_data(current_user=user, partner_id="psl")

    assert result == []


@pytest.mark.django_db
def test_get_partner_data_invalid_notifications(user: User) -> None:
    # invalid item_generic_status
    Notification.objects.create(
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

    result = get_partner_data(current_user=user, partner_id="psl")

    assert result == []


@pytest.mark.django_db
def test_get_partner_data(user: User) -> None:
    notification1 = Notification.objects.create(
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
    Notification.objects.create(  # notification 2
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
    notification3 = Notification.objects.create(
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

    notification4 = Notification.objects.create(
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

    notification5 = Notification.objects.create(
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
    notification6 = Notification.objects.create(
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

    Notification.objects.create(  # Other notification
        user_id=user.id,
        content_body="other notification",
        content_title="Other Notification title",
        item_type="unknown",
        item_id="42",
        sender="PSL",
        partner_id="psl",
    )

    result = get_partner_data(current_user=user, partner_id="psl")

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


@pytest.mark.django_db
def test_get_psl_inventory(user: User, monkeypatch: pytest.MonkeyPatch) -> None:
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
    data_mock = mock.Mock(return_value=items)
    monkeypatch.setattr("ami.partner.models.get_partner_data", data_mock)
    result = get_psl_inventory(current_user=user)
    assert result == FollowUpInventory(status=FollowUpInventoryStatus.SUCCESS, items=items)
