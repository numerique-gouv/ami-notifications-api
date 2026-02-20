from typing import Any

import pytest
from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
)
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_generate_partner_url_when_url_has_no_template(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    login(user, test_client)
    monkeypatch.setattr("app.env.PUBLIC_OTV_URL", "fake-public-otv-url")

    # When
    url = (
        "/api/v1/partner/otv/url?preferred_username=Delaforêt&email=wossewodda-37228@yopmail.com"
        "&address_city=Paris&address_postcode=75007&address_name=20 Avenue de Ségur"
    )
    response = test_client.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"partner_url": "fake-public-otv-url"}


async def test_generate_partner_url_when_url_has_template(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    login(user, test_client)

    url = (
        "/api/v1/partner/otv/url?preferred_username=Delaforêt&email=wossewodda-37228@yopmail.com"
        "&address_city=Paris&address_postcode=75007&address_name=20 Avenue de Ségur"
    )

    def generate_identity_token_mock(*args: Any, **kwargs: Any) -> str:
        return "fake.jwt.token"

    monkeypatch.setattr(
        "app.controllers.partner.generate_identity_token", generate_identity_token_mock
    )

    # Given
    monkeypatch.setattr("app.env.PUBLIC_OTV_URL", "fake-public-otv-url?caller={token-jwt}")
    monkeypatch.setattr("app.env.OTV_PRIVATE_KEY", "")
    monkeypatch.setattr("app.env.PSL_OTV_PUBLIC_KEY", "")

    # When
    response = test_client.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"partner_url": "fake-public-otv-url?"}

    # Given
    monkeypatch.setattr("app.env.OTV_PRIVATE_KEY", "foo")
    monkeypatch.setattr("app.env.PSL_OTV_PUBLIC_KEY", "")

    # When
    response = test_client.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"partner_url": "fake-public-otv-url?"}

    # Given
    monkeypatch.setattr("app.env.OTV_PRIVATE_KEY", "")
    monkeypatch.setattr("app.env.PSL_OTV_PUBLIC_KEY", "foo")

    # When
    response = test_client.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"partner_url": "fake-public-otv-url?"}

    # Given
    monkeypatch.setattr("app.env.OTV_PRIVATE_KEY", "foo")
    monkeypatch.setattr("app.env.PSL_OTV_PUBLIC_KEY", "bar")

    # When
    response = test_client.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"partner_url": "fake-public-otv-url?caller=fake.jwt.token"}


async def test_generate_partner_url_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/api/v1/partner/otv/url", test_client)


async def test_get_partner_public_key(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    monkeypatch.setattr("app.env.PUBLIC_OTV_PUBLIC_KEY", "fake-public-otv-public-key")

    # When
    response = test_client.get("/api/v1/partner/otv/public_key")

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"public_key": "fake-public-otv-public-key"}
