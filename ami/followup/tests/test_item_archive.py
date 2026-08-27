import pytest
from django.utils.timezone import now

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
        partner_slug="psl",
    )
    notification2 = Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_slug="psl",
    )

    payload = {
        "is_archived": True,
    }
    response = app.post(
        "/api/v1/users/data/followup/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        payload,
    )
    assert response.json == {
        "source": "notifications",
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
        "/api/v1/users/data/followup/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        payload,
    )
    assert response.json == {
        "source": "notifications",
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
        "/api/v1/users/data/followup/item/notifications/psl:OperationTranquilliteVacances:42/archive",
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
        "/api/v1/users/data/followup/item/notifications/psl:OperationTranquilliteVacances:/archive",
        status=404,
    )
    app.post(
        "/api/v1/users/data/followup/item/notifications/psl:OperationTranquilliteVacances/archive",
        status=404,
    )
    app.post("/api/v1/users/data/followup/item/notifications/psl:/archive", status=404)
    app.post("/api/v1/users/data/followup/item/notifications/psl/archive", status=404)


@pytest.mark.django_db
def test_archive_notification_item_wrong_source(
    user: User,
    app,
) -> None:
    login(app, user)

    payload = {
        "is_archived": True,
    }
    app.post(
        "/api/v1/users/data/followup/item/other/psl:OperationTranquilliteVacances:42/archive",
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
        partner_slug="psl",
    )
    # no item_status_label
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_slug="psl",
    )
    # no item_type
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_id="42",
        partner_slug="psl",
    )
    # no item_id
    Notification.objects.create(
        user_id=user.id,
        content_body="notification 1",
        content_title="Notification title 1",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        partner_slug="psl",
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
        partner_slug="psl",
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
        partner_slug="other",
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
        partner_slug="psl",
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
        partner_slug="psl",
    )

    payload = {
        "is_archived": True,
    }
    app.post(
        "/api/v1/users/data/followup/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        payload,
        status=404,
    )

    for notification in Notification.objects.all():
        assert notification.item_is_archived is None


@pytest.mark.django_db
def test_archive_notification_item_notification_not_found_has_sub_items(
    user: User,
    app,
) -> None:
    login(app, user)

    # only one sub item, parent item is unknown
    sub_notification1 = Notification.objects.create(
        user_id=user.id,
        content_body="sub notification 1",
        content_title="Sub Notification title 1",
        item_parent_partner_slug="dinum-ami",
        item_parent_type="JeDemenage",
        item_parent_id="40",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="JeDemenageCAF",
        item_id="44",
        partner_slug="dinum-ami",
    )
    payload = {
        "is_archived": True,
    }
    app.post(
        "/api/v1/users/data/followup/item/notifications/dinum-ami:JeDemenage:40/archive",
        payload,
        status=404,
    )
    assert Notification.objects.count() == 1
    sub_notification1.refresh_from_db()
    assert sub_notification1.item_is_archived is None

    # many sub notifications, but still only one sub item
    sub_notification2 = Notification.objects.create(
        user_id=user.id,
        content_body="sub notification 2",
        content_title="Sub Notification title 2",
        item_parent_partner_slug="dinum-ami",
        item_parent_type="JeDemenage",
        item_parent_id="40",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="JeDemenageCAF",
        item_id="44",
        partner_slug="dinum-ami",
    )
    app.post(
        "/api/v1/users/data/followup/item/notifications/dinum-ami:JeDemenage:40/archive",
        payload,
        status=404,
    )
    assert Notification.objects.count() == 2
    sub_notification1.refresh_from_db()
    sub_notification2.refresh_from_db()
    assert sub_notification1.item_is_archived is None
    assert sub_notification2.item_is_archived is None

    # more than one sub item
    sub_notification3 = Notification.objects.create(
        user_id=user.id,
        content_body="sub notification 3",
        content_title="Sub Notification title 3",
        item_parent_partner_slug="dinum-ami",
        item_parent_type="JeDemenage",
        item_parent_id="40",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="JeDemenageOther",
        item_id="45",
        partner_slug="dinum-ami",
    )
    response = app.post(
        "/api/v1/users/data/followup/item/notifications/dinum-ami:JeDemenage:40/archive",
        payload,
    )
    assert response.json == {
        "source": "notifications",
        "item_external_id": "dinum-ami:JeDemenage:40",
        "is_archived": True,
    }

    assert Notification.objects.count() == 4
    sub_notification1.refresh_from_db()
    sub_notification2.refresh_from_db()
    sub_notification3.refresh_from_db()
    assert sub_notification1.item_is_archived is None
    assert sub_notification2.item_is_archived is None
    assert sub_notification3.item_is_archived is None

    parent_notification = Notification.objects.latest("created_at")
    assert parent_notification.user.id == user.id
    assert parent_notification.content_body == ""
    assert parent_notification.content_private_body is None
    assert parent_notification.content_title == ""
    assert parent_notification.content_subheading is None
    assert parent_notification.content_icon is None
    assert parent_notification.content_link is None
    assert parent_notification.item_type == "JeDemenage"
    assert parent_notification.item_id == "40"
    assert parent_notification.item_parent_partner_slug is None
    assert parent_notification.item_parent_type is None
    assert parent_notification.item_parent_id is None
    assert parent_notification.item_status_label == "Nouveau"
    assert parent_notification.item_generic_status == "new"
    assert parent_notification.item_milestone_start_date is None
    assert parent_notification.item_milestone_end_date is None
    assert parent_notification.item_canal is None
    assert parent_notification.item_is_archived is True
    assert parent_notification.event_date < now()
    assert parent_notification.valid_until < now()
    assert parent_notification.partner_slug == "dinum-ami"
    assert parent_notification.try_push is False
    assert parent_notification.send_status is False
    assert parent_notification.read is False


@pytest.mark.django_db
def test_archive_item_without_auth(app) -> None:
    assert_query_fails_without_auth(
        app,
        "/api/v1/users/data/followup/item/notifications/psl:OperationTranquilliteVacances:42/archive",
        method="post",
    )
