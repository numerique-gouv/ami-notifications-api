from typing import Any

import pytest
from rest_framework.status import HTTP_200_OK

from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_generate_partner_url_when_no_query_parameters(
    django_app,
    user: User,
    settings,
) -> None:
    # Given
    login(django_app, user)
    settings.CONFIG["PARTNERS_PSL_OTV_REQUEST_URL"] = "fake-public-otv-url"

    # When
    response = django_app.get(
        "/api/v1/partner/otv/url?preferred_username=&email=&address_city=&address_postcode=&address_name="
    )

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url"}


@pytest.mark.django_db
def test_generate_partner_url_when_url_has_no_template(
    django_app,
    user: User,
    settings,
) -> None:
    # Given
    login(django_app, user)
    settings.CONFIG["PARTNERS_PSL_OTV_REQUEST_URL"] = "fake-public-otv-url"

    # When
    response = django_app.get(
        "/api/v1/partner/otv/url?preferred_username=Delaforêt&email=wossewodda-37228@yopmail.com&address_city=Paris&address_postcode=75007&address_name=20 Avenue de Ségur"
    )

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url"}


@pytest.mark.django_db
def test_generate_partner_url_when_url_has_template(
    django_app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    login(django_app, user)

    url = "/api/v1/partner/otv/url?preferred_username=Delaforêt&email=wossewodda-37228@yopmail.com&address_city=Paris&address_postcode=75007&address_name=20 Avenue de Ségur"

    def mock_generate_identity_token(*args: Any, **kwargs: Any):
        return "fake-identity-token"

    monkeypatch.setattr(
        "ami.partner.api_views.generate_identity_token",
        mock_generate_identity_token,
    )

    # Given
    settings.CONFIG["PARTNERS_PSL_OTV_REQUEST_URL"] = "fake-public-otv-url?caller={token-jwt}"
    settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PFX_B64"] = ""
    settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"] = ""

    # When
    response = django_app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?"}

    # Given
    settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PFX_B64"] = "foo"
    settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"] = ""

    # When
    response = django_app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?"}

    # Given
    settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PFX_B64"] = ""
    settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"] = "foo"

    # When
    response = django_app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?"}

    # Given
    settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PFX_B64"] = "foo"
    settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"] = "bar"

    # When
    response = django_app.get(url)

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"partner_url": "fake-public-otv-url?caller=fake-identity-token"}


@pytest.mark.django_db
def test_generate_partner_url_without_auth(
    django_app,
) -> None:
    assert_query_fails_without_auth(django_app, "/api/v1/partner/otv/url")


@pytest.mark.django_db
def test_get_partner_public_key(
    django_app,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    # Given
    settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PUBLIC_KEY"] = "fake-public-otv-public-key"

    # When
    response = django_app.get("/api/v1/partner/otv/public_key")

    # Then
    assert response.status_code == HTTP_200_OK
    assert response.json == {"public_key": "fake-public-otv-public-key"}
