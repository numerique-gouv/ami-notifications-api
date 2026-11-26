import datetime
from typing import Any
from unittest import mock

import pytest

from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import PersonalDataConsent, User


@pytest.mark.django_db
def test_get_services_items_parameters_empty_payload(
    app,
    user: User,
) -> None:
    login(app, user)

    response = app.post_json("/api/v1/users/data/services/item/parameters")
    assert response.json == {"data": {}}

    response = app.post_json("/api/v1/users/data/services/item/parameters", {"parameters": []})
    assert response.json == {"data": {}}


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token__when_consent(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    login(app, user)

    consent_datetime = datetime.datetime(2020, 12, 25, 17, 5, 55, tzinfo=datetime.timezone.utc)
    PersonalDataConsent.objects.create(user=user, consent_datetime=consent_datetime)
    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "bar"

    mock_generate_identity_token = mock.Mock(return_value="fake-identity-token")

    monkeypatch.setattr(
        "ami.service.serializers.generate_identity_token",
        mock_generate_identity_token,
    )

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {
                    "preferred_username": "Delaforêt",
                    "email": "wossewodda-37228@yopmail.com",
                    "address_city": "Paris",
                    "address_postcode": "75007",
                    "address_citycode": "75107",
                    "address_name": "20 Avenue de Ségur",
                },
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": "fake-identity-token"}}
    assert mock_generate_identity_token.call_args_list == [
        mock.call(
            "Delaforêt",
            "wossewodda-37228@yopmail.com",
            "Paris",
            "75007",
            "75107",
            "20 Avenue de Ségur",
            "651d806d65788bc260faa89a555fdf89bd573a5c9a4d8bb897967e14951ab65d",
        )
    ]


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token__when_consent_not_given(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    login(app, user)

    PersonalDataConsent.objects.create(user=user, consent_datetime=None)
    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "bar"

    mock_generate_identity_token = mock.Mock(return_value="fake-identity-token")

    monkeypatch.setattr(
        "ami.service.serializers.generate_identity_token",
        mock_generate_identity_token,
    )

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {
                    "preferred_username": "Delaforêt",
                    "email": "wossewodda-37228@yopmail.com",
                    "address_city": "Paris",
                    "address_postcode": "75007",
                    "address_citycode": "75107",
                    "address_name": "20 Avenue de Ségur",
                },
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": "fake-identity-token"}}
    assert mock_generate_identity_token.call_args_list == [
        mock.call(
            "",
            "",
            "",
            "",
            "",
            "",
            "651d806d65788bc260faa89a555fdf89bd573a5c9a4d8bb897967e14951ab65d",
        )
    ]


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token__when_consent_does_not_exist(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    login(app, user)

    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "bar"

    mock_generate_identity_token = mock.Mock(return_value="fake-identity-token")

    monkeypatch.setattr(
        "ami.service.serializers.generate_identity_token",
        mock_generate_identity_token,
    )

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {
                    "preferred_username": "Delaforêt",
                    "email": "wossewodda-37228@yopmail.com",
                    "address_city": "Paris",
                    "address_postcode": "75007",
                    "address_citycode": "75107",
                    "address_name": "20 Avenue de Ségur",
                },
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": "fake-identity-token"}}
    assert mock_generate_identity_token.call_args_list == [
        mock.call(
            "",
            "",
            "",
            "",
            "",
            "",
            "651d806d65788bc260faa89a555fdf89bd573a5c9a4d8bb897967e14951ab65d",
        )
    ]


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token_missing_payload(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    login(app, user)

    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "bar"

    def mock_generate_identity_token(*args: Any, **kwargs: Any):
        return "fake-identity-token"

    monkeypatch.setattr(
        "ami.service.serializers.generate_identity_token",
        mock_generate_identity_token,
    )

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {},
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": "fake-identity-token"}}


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token_empty_fields(
    app,
    user: User,
    monkeypatch: pytest.MonkeyPatch,
    settings,
) -> None:
    login(app, user)

    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "bar"

    def mock_generate_identity_token(*args: Any, **kwargs: Any):
        return "fake-identity-token"

    monkeypatch.setattr(
        "ami.service.serializers.generate_identity_token",
        mock_generate_identity_token,
    )

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {
                    "preferred_username": "",
                    "email": "",
                    "address_city": "",
                    "address_postcode": "",
                    "address_citycode": "",
                    "address_name": "",
                },
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": "fake-identity-token"}}


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token_missing_otv_keys(
    app,
    user: User,
    settings,
) -> None:
    login(app, user)

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {
                    "preferred_username": "Delaforêt",
                    "email": "wossewodda-37228@yopmail.com",
                    "address_city": "Paris",
                    "address_postcode": "75007",
                    "address_citycode": "75107",
                    "address_name": "20 Avenue de Ségur",
                },
            }
        ]
    }

    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = ""
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = ""
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": ""}}

    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = "foo"
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = ""
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": ""}}

    settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64 = ""
    settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY = "foo"
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": ""}}


@pytest.mark.django_db
def test_get_services_items_parameters_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(
        app, "/api/v1/users/data/services/item/parameters", method="post_json"
    )
