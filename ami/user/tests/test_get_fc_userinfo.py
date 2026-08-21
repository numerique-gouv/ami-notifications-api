from typing import Any

import pytest
from django.conf import settings

from ami.notification.models import ScheduledNotification
from ami.user.data import get_fc_userinfo
from ami.user.models import User
from ami.utils.httpx import httpxAsyncClient


@pytest.fixture
def mock_jwk_client(monkeypatch):
    class FakeJwkClient:
        def __init__(self, url):
            pass

        def get_signing_key_from_jwt(self, token):
            return "stub-signing-key"

    monkeypatch.setattr("jwt.PyJWKClient", FakeJwkClient)


@pytest.mark.django_db
async def test_get_fc_userinfo(monkeypatch, httpx_mock, userinfo, mock_jwk_client):
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    httpx_mock.add_response(
        url=f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_USERINFO_ENDPOINT}", text="XXX"
    )

    async with httpxAsyncClient() as httpx_async_client:
        user_decoded_info, user_id = await get_fc_userinfo(
            token_type="token-type",
            access_token="access-token",
            httpx_async_client=httpx_async_client,
        )

    assert user_decoded_info["decoded_user_data"]["given_name"] == userinfo["given_name"]
    assert await User.objects.acount() == 1
    assert await User.objects.filter(id=user_id).acount() == 1
    assert await ScheduledNotification.objects.filter(user_id=user_id).acount() == 1

    # second login
    httpx_mock.add_response(
        url=f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_USERINFO_ENDPOINT}", text="XXX"
    )

    async with httpxAsyncClient() as httpx_async_client:
        user_decoded_info, user_id = await get_fc_userinfo(
            token_type="token-type",
            access_token="access-token",
            httpx_async_client=httpx_async_client,
        )

    assert await User.objects.acount() == 1
    assert await User.objects.filter(id=user_id).acount() == 1
    assert await ScheduledNotification.objects.filter(user_id=user_id).acount() == 1


@pytest.mark.django_db
async def test_get_fc_userinfo_no_create_user(monkeypatch, httpx_mock, userinfo, mock_jwk_client):
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    await ScheduledNotification.objects.all().adelete()
    await User.objects.all().adelete()

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    httpx_mock.add_response(
        url=f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_USERINFO_ENDPOINT}", text="XXX"
    )

    async with httpxAsyncClient() as httpx_async_client:
        user_decoded_info, user_id = await get_fc_userinfo(
            token_type="token-type",
            access_token="access-token",
            httpx_async_client=httpx_async_client,
            create_user=False,
        )

    assert user_decoded_info["decoded_user_data"]["given_name"] == userinfo["given_name"]
    assert not user_id
    assert await User.objects.acount() == 0
    assert await ScheduledNotification.objects.filter(user_id=user_id).acount() == 0
