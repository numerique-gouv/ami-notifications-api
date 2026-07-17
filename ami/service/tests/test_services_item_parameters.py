from typing import Any

import pytest

from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


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
def test_get_services_items_parameters_otv_jwt_token(
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
                    "preferred_username": "Delaforêt",
                    "email": "wossewodda-37228@yopmail.com",
                    "address_city": "Paris",
                    "address_postcode": "75007",
                    "address_name": "20 Avenue de Ségur",
                },
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": "fake-identity-token"}}


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token_missing_payload(
    app,
    user: User,
) -> None:
    login(app, user)

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {},
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": ""}}


@pytest.mark.django_db
def test_get_services_items_parameters_otv_jwt_token_empty_fields(
    app,
    user: User,
) -> None:
    login(app, user)

    parameters_data = {
        "parameters": [
            {
                "parameter": "otv_jwt_token",
                "values": {
                    "preferred_username": "",
                    "email": "",
                    "address_city": "",
                    "address_postcode": "",
                    "address_name": "",
                },
            }
        ]
    }
    response = app.post_json("/api/v1/users/data/services/item/parameters", parameters_data)
    assert response.json == {"data": {"otv_jwt_token": ""}}


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
