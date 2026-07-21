import datetime
import uuid
from typing import Any

import pytest

from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import Registration, User


@pytest.mark.django_db
def test_register_webpush(app, user: User, webpushsubscription: dict[str, Any]) -> None:
    login(app, user)

    assert Registration.objects.count() == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "subscription": webpushsubscription,
    }
    app.post_json("/api/v1/users/registrations", register_data, status=201)

    assert Registration.objects.count() == 1
    registration = Registration.objects.get()
    registration_id = registration.id

    # Second registration, we're expecting a 200 OK, not 201 CREATED.
    register_data = {
        "subscription": webpushsubscription,
    }
    app.post_json("/api/v1/users/registrations", register_data, status=200)

    assert Registration.objects.count() == 1
    registration = Registration.objects.get()
    assert registration.id == registration_id


@pytest.mark.django_db
def test_register_mobile_app(app, user: User, mobileAppSubscription: dict[str, Any]) -> None:
    login(app, user)

    assert Registration.objects.count() == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "subscription": mobileAppSubscription,
    }
    app.post_json("/api/v1/users/registrations", register_data, status=201)

    assert Registration.objects.count() == 1

    # Second registration, we're expecting a 200 OK, not 201 CREATED.
    register_data = {"subscription": mobileAppSubscription}
    app.post_json("/api/v1/users/registrations", register_data, status=200)

    assert Registration.objects.count() == 1


@pytest.mark.django_db
def test_register_mobile_app_existing_registration_different_device(
    app, user: User, mobileAppSubscription: dict[str, Any]
) -> None:
    login(app, user)

    assert Registration.objects.count() == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "subscription": mobileAppSubscription,
    }
    app.post_json("/api/v1/users/registrations", register_data, status=201)

    assert Registration.objects.count() == 1

    # Second registration, difference device, we're expecting a 201 CREATED.
    mobileAppSubscription["device_id"] = "some other device"
    register_data = {"subscription": mobileAppSubscription}
    app.post_json("/api/v1/users/registrations", register_data, status=201)

    assert Registration.objects.count() == 2


@pytest.mark.django_db
def test_register_mobile_app_different_registration_same_device(
    app, user: User, mobileAppSubscription: dict[str, Any]
) -> None:
    login(app, user)

    assert Registration.objects.count() == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "subscription": mobileAppSubscription,
    }
    app.post_json("/api/v1/users/registrations", register_data, status=201)

    assert Registration.objects.count() == 1

    # Second registration, same device, we're expecting a 200 CREATED, but only one remaining registration.
    mobileAppSubscription["fcm_token"] = "some other token"
    register_data = {"subscription": mobileAppSubscription}
    app.post_json("/api/v1/users/registrations", register_data, status=200)

    assert Registration.objects.count() == 1
    registration = Registration.objects.get()
    assert registration.subscription["fcm_token"] == "some other token"


@pytest.mark.django_db
def test_register_fields(app, user: User, webpushsubscription: dict[str, Any]) -> None:
    login(app, user)

    # id, created_at and updated_at are ignored
    registration_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    registration_id: uuid.UUID = uuid.uuid4()
    registration_data = {
        "subscription": webpushsubscription,
        "id": str(registration_id),
        "created_at": registration_date.isoformat(),
        "updated_at": registration_date.isoformat(),
    }
    app.post_json("/api/v1/users/registrations", registration_data, status=201)

    assert Registration.objects.count() == 1
    registration = Registration.objects.get()
    assert registration.id != registration_id
    assert registration.created_at < registration_date
    assert registration.updated_at < registration_date


@pytest.mark.django_db
def test_register_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/registrations", method="post")


@pytest.mark.django_db
def test_unregister_legacy(app, webpush_registration: Registration) -> None:
    login(app, webpush_registration.user)

    assert Registration.objects.count() == 1

    app.delete(f"/api/v1/users/registrations/{webpush_registration.id}", status=204)

    assert Registration.objects.count() == 0

    # registration does not exist
    app.delete(f"/api/v1/users/registrations/{webpush_registration.id}", status=404)

    # registration of another user than current user
    other_user = User.objects.create(fc_hash="fc-hash")
    Registration.objects.create(user_id=other_user.id)  # Other registration
    app.delete(f"/api/v1/users/registrations/{webpush_registration.id}", status=404)


@pytest.mark.django_db
def test_unregister_legacy_without_auth(app, webpush_registration: Registration) -> None:
    assert_query_fails_without_auth(
        app,
        f"/api/v1/users/registrations/{webpush_registration.id}",
        method="delete",
    )


@pytest.mark.django_db
def test_unregister(app, user: User) -> None:
    login(app, user)

    user_1 = User.objects.create(fc_hash="fc-hash-1")
    user_2 = User.objects.create(fc_hash="fc-hash-2")
    user_3 = User.objects.create(fc_hash="fc-hash-3")
    device_id_1 = "fake-device-id-1"
    device_id_2 = "fake-device-id-2"
    device_id_3 = "fake-device-id-3"
    Registration.objects.create(user_id=user_1.id, device_id=device_id_1)
    Registration.objects.create(user_id=user_2.id, device_id=device_id_2)
    Registration.objects.create(user_id=user_3.id, device_id=device_id_1)

    assert Registration.objects.count() == 3

    payload = {"device_id": device_id_1}
    app.put("/api/v1/users/registrations?action=removeFromDeviceId", payload, status=200)

    assert Registration.objects.count() == 1

    # registration does not exist
    payload = {"device_id": device_id_1}
    app.put("/api/v1/users/registrations?action=removeFromDeviceId", payload, status=404)

    # registration of another user than current user
    user_4 = User.objects.create(fc_hash="fc-hash-4")
    Registration.objects.create(user_id=user_4.id, device_id=device_id_3)
    payload = {"device_id": device_id_1}
    app.put("/api/v1/users/registrations?action=removeFromDeviceId", payload, status=404)


@pytest.mark.django_db
def test_unregister_should_log_error_when_action_is_not_remove_from_device_id(
    app, user: User, caplog
) -> None:
    login(app, user)

    caplog.clear()
    caplog.set_level("ERROR")

    user = User.objects.create(fc_hash="fc-hash")
    device_id = "fake-device-id"
    other_device_id = "fake-other-device-id"
    Registration.objects.create(user_id=user.id, device_id=device_id)

    assert Registration.objects.count() == 1

    payload = {"device_id": other_device_id}
    response = app.put("/api/v1/users/registrations?action=wrongAction", payload, status=400)

    assert response.json == {
        "action": ["«\xa0wrongAction\xa0» n'est pas un choix valide."],
    }


@pytest.mark.django_db
def test_unregister_should_log_error_when_no_registration_found(app, user: User, caplog) -> None:
    login(app, user)

    caplog.clear()
    caplog.set_level("ERROR")

    user = User.objects.create(fc_hash="fc-hash")
    device_id = "fake-device-id"
    other_device_id = "fake-other-device-id"
    Registration.objects.create(user_id=user.id, device_id=device_id)

    assert Registration.objects.count() == 1

    payload = {"device_id": other_device_id}
    app.put("/api/v1/users/registrations?action=removeFromDeviceId", payload, status=404)

    assert any("No registration for the device_id" in record.message for record in caplog.records)


@pytest.mark.django_db
def test_unregister_without_auth(app, user: User) -> None:
    assert_query_fails_without_auth(
        app,
        "/api/v1/users/registrations?action=removeFromDeviceId",
        method="put",
    )


@pytest.mark.django_db
def test_list_registrations(app, webpush_registration: Registration) -> None:
    login(app, webpush_registration.user)

    response = app.get("/api/v1/users/registrations", status=200)
    registrations = response.json
    assert len(registrations) == 1
    assert set(response.json[0].keys()) == {"id", "user_id", "subscription", "created_at"}
    assert response.json[0]["id"] == str(webpush_registration.id)
    assert response.json[0]["user_id"] == str(webpush_registration.user.id)
    assert response.json[0]["subscription"] == webpush_registration.subscription
    assert response.json[0]["created_at"] == webpush_registration.created_at.isoformat().replace(
        "+00:00", "Z"
    )


@pytest.mark.django_db
def test_list_registrations_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/registrations")
