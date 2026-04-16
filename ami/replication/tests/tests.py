import pytest

from ami.replication.models import AnonymizedUser
from ami.user.models import User


@pytest.mark.django_db
def test_anonymized_user_does_not_have_fc_hash(user: User) -> None:
    anonymized = AnonymizedUser.from_user(user)
    assert not hasattr(anonymized, "fc_hash")
    assert hasattr(anonymized, "last_logged_in")
    assert hasattr(anonymized, "created_at")
    assert hasattr(anonymized, "updated_at")
