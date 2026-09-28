from unittest import mock

import pytest

from ami.utils.sentry import set_sentry_user


@pytest.mark.django_db
def test_set_sentry_user(user, monkeypatch):
    set_user_mock = mock.Mock()
    monkeypatch.setattr("sentry_sdk.set_user", set_user_mock)
    set_sentry_user(user)
    assert set_user_mock.call_args[0][0] == {"id": "5c441b58f2ec32f182b9"}
