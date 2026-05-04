import pytest

from ami.notification.models import Notification
from ami.replication.app import (
    replicate_anonymized_notifications,
    replicate_anonymized_registrations,
    replicate_anonymized_users,
)
from ami.replication.models import AnonymizedNotification, AnonymizedRegistration, AnonymizedUser
from ami.user.models import Registration, User


@pytest.mark.django_db
def test_anonymized_user_does_not_have_fc_hash(user: User) -> None:
    anonymized = AnonymizedUser.from_user(user)
    assert not hasattr(anonymized, "fc_hash")
    assert hasattr(anonymized, "last_logged_in")
    assert hasattr(anonymized, "created_at")
    assert hasattr(anonymized, "updated_at")


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_users(two_users: list[User]) -> None:
    replicate_anonymized_users()

    assert AnonymizedUser.objects.using("data_ware_house").count() == 2
    for user in two_users:
        anonymized = AnonymizedUser.objects.using("data_ware_house").get(id=user.id)
        assert anonymized.last_logged_in == user.last_logged_in
        assert anonymized.created_at == user.created_at
        assert anonymized.updated_at == user.updated_at


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_users_processes_by_batch(two_users: list[User]) -> None:
    replicate_anonymized_users(chunk_size=1)

    assert AnonymizedUser.objects.using("data_ware_house").count() == 2
    for user in two_users:
        assert AnonymizedUser.objects.using("data_ware_house").filter(id=user.id).exists()


@pytest.mark.django_db
def test_anonymized_notification_does_not_have_user(notification: Notification) -> None:
    anonymized = AnonymizedNotification.from_notification(notification)
    assert not hasattr(anonymized, "user")
    assert hasattr(anonymized, "content_title")
    assert hasattr(anonymized, "content_body")
    assert hasattr(anonymized, "created_at")
    assert hasattr(anonymized, "updated_at")


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_notifications(notification: Notification) -> None:
    replicate_anonymized_notifications()

    anonymized = AnonymizedNotification.objects.using("data_ware_house").get(id=notification.id)
    assert anonymized.content_title == notification.content_title
    assert anonymized.content_body == notification.content_body
    assert anonymized.created_at == notification.created_at
    assert anonymized.updated_at == notification.updated_at


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_notifications_processes_by_batch(notification: Notification) -> None:
    Notification.objects.create(
        user_id=notification.user_id,
        content_body="Second notification",
        content_title="Second title",
    )
    replicate_anonymized_notifications(chunk_size=1)

    assert AnonymizedNotification.objects.using("data_ware_house").count() == 2


@pytest.mark.django_db
def test_anonymized_registration_does_not_have_user_nor_subscription(
    webpush_registration: Registration,
) -> None:
    anonymized = AnonymizedRegistration.from_registration(webpush_registration)
    assert not hasattr(anonymized, "user")
    assert not hasattr(anonymized, "subscription")
    assert hasattr(anonymized, "created_at")
    assert hasattr(anonymized, "updated_at")


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_registrations(webpush_registration: Registration) -> None:
    replicate_anonymized_registrations()

    anonymized = AnonymizedRegistration.objects.using("data_ware_house").get(
        id=webpush_registration.id
    )
    assert anonymized.created_at == webpush_registration.created_at
    assert anonymized.updated_at == webpush_registration.updated_at


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_registrations_processes_by_batch(
    user: User,
    webpush_registration: Registration,
    mobileAppSubscription: dict,  # noqa: ARG001
) -> None:
    Registration.objects.create(user=user, subscription=mobileAppSubscription)
    replicate_anonymized_registrations(chunk_size=1)

    assert AnonymizedRegistration.objects.using("data_ware_house").count() == 2
