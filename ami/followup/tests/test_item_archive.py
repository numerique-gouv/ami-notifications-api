import pytest

from ami.notification.models import Notification
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_archive_notification_item(
    user: User,
    app,
) -> None:
    login(app, user)

    notification1 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    notification2 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )

    payload = {
        "is_archived": True,
    }
    response = app.post(
        "/api/v1/users/follow-up/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        payload,
    )
    assert response.json == {
        "inventory": "notifications",
        "item_external_id": "psl:OperationTranquilliteVacances:42",
        "is_archived": True,
    }

    notification1.refresh_from_db()
    notification2.refresh_from_db()
    assert notification1.item_is_archived is None
    assert notification2.item_is_archived is True

    payload = {
        "is_archived": False,
    }
    response = app.post(
        "/api/v1/users/follow-up/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        payload,
    )
    assert response.json == {
        "inventory": "notifications",
        "item_external_id": "psl:OperationTranquilliteVacances:42",
        "is_archived": False,
    }

    notification1.refresh_from_db()
    notification2.refresh_from_db()
    assert notification1.item_is_archived is None
    assert notification2.item_is_archived is False


@pytest.mark.django_db
def test_archive_notification_item_empty_payload(
    user: User,
    app,
) -> None:
    login(app, user)

    response = app.post(
        "/api/v1/users/follow-up/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        status=400,
    )
    assert response.json == {
        "is_archived": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_archive_notification_item_wrong_id(
    user: User,
    app,
) -> None:
    login(app, user)

    app.post(
        "/api/v1/users/follow-up/item/notifications/psl:OperationTranquilliteVacances:/archive",
        status=404,
    )
    app.post(
        "/api/v1/users/follow-up/item/notifications/psl:OperationTranquilliteVacances/archive",
        status=404,
    )
    app.post("/api/v1/users/follow-up/item/notifications/psl:/archive", status=404)
    app.post("/api/v1/users/follow-up/item/notifications/psl/archive", status=404)


@pytest.mark.django_db
def test_archive_notification_item_wrong_inventory(
    user: User,
    app,
) -> None:
    login(app, user)

    payload = {
        "is_archived": True,
    }
    app.post(
        "/api/v1/users/follow-up/item/other/psl:OperationTranquilliteVacances:42/archive",
        payload,
        status=404,
    )


@pytest.mark.django_db
def test_archive_notification_item_notification_not_found(
    user: User,
    app,
) -> None:
    login(app, user)

    # no item_generic_status
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
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
        partner_id="psl",
    )
    # other user
    other_user = User.objects.create(fc_hash="fc-hash")
    Notification.objects.create(
        user_id=other_user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    # other partner_id
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="other",
    )
    # other item_type
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="Other",
        item_id="42",
        partner_id="psl",
    )
    # other item_id
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="44",
        partner_id="psl",
    )

    payload = {
        "inventory": "notifications",
        "is_archived": True,
    }
    app.post(
        "/api/v1/users/follow-up/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        payload,
        status=404,
    )

    for notification in Notification.objects.all():
        assert notification.item_is_archived is None


@pytest.mark.django_db
def test_archive_item_without_auth(app) -> None:
    assert_query_fails_without_auth(
        app,
        "/api/v1/users/follow-up/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        method="post",
    )
