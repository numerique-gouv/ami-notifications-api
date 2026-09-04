import datetime
from typing import Any
from unittest import mock

import pytest
from rest_framework.status import HTTP_200_OK

from ami.partner.models import Partner
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_generate_partner_url_when_no_query_parameters(
    app,
    user: User,
    settings,
) -> None:
    # Given
    login(app, user)
    settings.PARTNERS_PSL_OTV_REQUEST_URL = "fake-public-otv-url"

    # When
    response = app.get(
        "/api/v1/partner/otv/url?preferred_username=&email=&address_city=&address_postcode=&address_name="
    )

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url"}


@pytest.mark.django_db
def test_generate_partner_url_when_url_has_no_template(
    app,
    user: User,
    settings,
) -> None:
    # Given
    login(app, user)
    settings.PARTNERS_PSL_OTV_REQUEST_URL = "fake-public-otv-url"

    # When
    response = app.get(
        "/api/v1/partner/otv/url?preferred_username=Delaforêt&email=wossewodda-37228@yopmail.com&address_city=Paris&address_postcode=75007&address_name=20 Avenue de Ségur"
    )

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url"}


@pytest.mark.django_db
def test_generate_partner_url_when_url_has_template(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    login(app, user)

    url = "/api/v1/partner/otv/url?preferred_username=Delaforêt&email=wossewodda-37228@yopmail.com&address_city=Paris&address_postcode=75007&address_name=20 Avenue de Ségur"

    def mock_generate_identity_token(*args: Any, **kwargs: Any):
        return "fake-identity-token"

    monkeypatch.setattr(
        "ami.partner.api_views.generate_identity_token",
        mock_generate_identity_token,
    )

    # Given
    settings.PARTNERS_PSL_OTV_REQUEST_URL = "fake-public-otv-url?caller={token-jwt}"
    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = ""
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = ""

    # When
    response = app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?"}

    # Given
    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = ""

    # When
    response = app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?"}

    # Given
    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = ""
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "foo"

    # When
    response = app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?"}

    # Given
    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "bar"

    # When
    response = app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?caller=fake-identity-token"}


@pytest.mark.django_db
def test_generate_partner_url_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(app, "/api/v1/partner/otv/url")


@pytest.mark.django_db
def test_get_partner_public_key(
    app,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    # Given
    settings.PARTNERS_PSL_OTV_JWT_CERT_PUBLIC_KEY = "fake-public-otv-public-key"

    # When
    response = app.get("/api/v1/partner/otv/public_key")

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"public_key": "fake-public-otv-public-key"}


@pytest.mark.django_db
def test_get_partners(app, user: User, monkeypatch: pytest.MonkeyPatch) -> None:
    login(app, user)

    duration_mock = mock.Mock(
        return_value=datetime.datetime(2026, 2, 14, 11, 16, tzinfo=datetime.timezone.utc)
    )
    monkeypatch.setattr(
        "ami.partner.api_views.DurationExpiration.compute_expires_at", duration_mock
    )

    Partner.objects.all().delete()
    Partner.objects.create(slug="new-1", name="New-1", consent_is_enabled=False)
    Partner.objects.create(slug="new-3", name="New-3", consent_is_enabled=True)
    Partner.objects.create(slug="new-2", name="New-2", consent_is_enabled=True)

    response = app.get("/api/v1/users/data/partners", status=200)
    assert response.json == {
        "status": "success",
        "items": [
            {
                "consent_is_enabled": True,
                "link": None,
                "name": "New-2",
                "slug": "new-2",
            },
            {
                "consent_is_enabled": True,
                "link": None,
                "name": "New-3",
                "slug": "new-3",
            },
        ],
        "expires_at": "2026-02-14T11:16:00Z",
    }


@pytest.mark.django_db
def test_get_partners_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/data/partners")
