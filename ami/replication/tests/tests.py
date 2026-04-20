import pytest

from ami.replication.app import replicate_anonymized_users
from ami.replication.models import AnonymizedUser
from ami.user.models import User


@pytest.mark.django_db
def test_anonymized_user_does_not_have_fc_hash(two_users: list[User]) -> None:
    anonymized = AnonymizedUser.from_user(two_users[0])
    assert not hasattr(anonymized, "fc_hash")
    assert hasattr(anonymized, "last_logged_in")
    assert hasattr(anonymized, "created_at")
    assert hasattr(anonymized, "updated_at")


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_users(two_users: list[User]) -> None:
    replicate_anonymized_users()

    assert AnonymizedUser.objects.using("data_ware_house").count() == 2
    for user in two_users:
        anonymized = AnonymizedUser.objects.using("data_ware_house").get(original_id=user.id)
        assert anonymized.last_logged_in == user.last_logged_in
        assert anonymized.created_at == user.created_at
        assert anonymized.updated_at == user.updated_at


@pytest.mark.django_db(databases=["default", "data_ware_house"])
def test_replicate_anonymized_users_processes_by_batch(two_users: list[User]) -> None:
    replicate_anonymized_users(chunk_size=1)

    assert AnonymizedUser.objects.using("data_ware_house").count() == 2
    for user in two_users:
        assert AnonymizedUser.objects.using("data_ware_house").filter(original_id=user.id).exists()
