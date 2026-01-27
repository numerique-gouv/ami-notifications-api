import datetime
from typing import Any, Dict
from uuid import UUID

import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime
from litestar import Litestar
from litestar.testing import TestClient

from app.utils import build_fc_hash, decode_identity_token, generate_identity_token


async def test_ping(
    test_client: TestClient[Litestar],
):
    response = test_client.head("/ping")
    assert response.status_code == 200


async def test_get_sector_identifier_url(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.env.PUBLIC_SECTOR_IDENTIFIER_URL", "  https://example.com  \nfoobar \n"
    )
    response = test_client.get("/sector_identifier_url")
    assert response.json() == ["https://example.com", "foobar"]


async def test_build_fc_hash(
    test_client: TestClient[Litestar],
) -> None:
    given_name = "Angela Claire Louise"
    family_name = "DUBOIS"
    birthdate = "1962-08-24"
    gender = "female"
    birthplace = "75107"
    birthcountry = "99100"
    response = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"

    birthplace = ""
    response = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    assert response == "7e74df2cbebae761eccedbc24b7fe589bb83137f7808a2930031f52c73d75efe"


@freeze_time("2026-01-23 10:36:00")
def test_generate_identity_token(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    preferred_username: str = "Delaforêt"
    email: str = "wossewodda-37228@yopmail.com"
    address_city: str = "Paris"
    address_postcode: str = "75007"
    address_name: str = "20 Avenue de Ségur"
    fc_hash: str = "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"

    mock_uuid_str = "550e8400-e29b-41d4-a716-446655440000"

    def mock_uuid_uuid4():
        return UUID(mock_uuid_str)

    mock_otv_private_key = "test_private_key"
    expected_token = "fake-generated-identity-token"

    def mock_jwt_encode(payload: Any, key: Any, **kwargs: Any) -> str:
        assert payload["iss"] == "ami"
        assert payload["iat"] == 1769164560
        assert payload["exp"] == FakeDatetime(2026, 1, 23, 11, 6, tzinfo=datetime.timezone.utc)
        assert payload["nonce"] == mock_uuid_str
        assert payload["hash_fc"] == fc_hash
        assert payload["data"] == {
            "nom_usage": preferred_username,
            "email": email,
            "commune_nom": address_city,
            "commune_cp": address_postcode,
            "commune_adresse": address_name,
        }
        assert key.decode() == mock_otv_private_key
        assert kwargs["algorithm"] == "RS256"
        return expected_token

    monkeypatch.setattr("app.utils.uuid4", mock_uuid_uuid4)
    monkeypatch.setattr("jwt.encode", mock_jwt_encode)
    monkeypatch.setattr("app.env.OTV_PRIVATE_KEY", mock_otv_private_key)

    # When
    token = generate_identity_token(
        preferred_username, email, address_city, address_postcode, address_name, fc_hash
    )

    # Then
    assert token == expected_token


@freeze_time("2026-01-23 10:36:00")
def test_generate_identity_token_with_decode(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
    rsa_keys: Dict[str, str],
) -> None:
    # Given
    preferred_username: str = "Delaforêt"
    email: str = "wossewodda-37228@yopmail.com"
    address_city: str = "Paris"
    address_postcode: str = "75007"
    address_name: str = "20 Avenue de Ségur"
    fc_hash: str = "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"

    mock_uuid_str = "550e8400-e29b-41d4-a716-446655440000"

    def mock_uuid_uuid4():
        return UUID(mock_uuid_str)

    monkeypatch.setattr("app.utils.uuid4", mock_uuid_uuid4)

    fake_otv_private_key: str = rsa_keys["private"]
    fake_otv_public_key: str = rsa_keys["public"]

    monkeypatch.setattr("app.utils.uuid4", mock_uuid_uuid4)
    monkeypatch.setattr("app.env.OTV_PRIVATE_KEY", fake_otv_private_key)
    monkeypatch.setattr("app.env.PUBLIC_OTV_PUBLIC_KEY", fake_otv_public_key)

    # When
    token = generate_identity_token(
        preferred_username, email, address_city, address_postcode, address_name, fc_hash
    )

    decoded_result = decode_identity_token(token)

    # Then
    assert decoded_result["iss"] == "ami"
    assert decoded_result["iat"] == 1769164560
    assert decoded_result["exp"] == 1769166360
    assert decoded_result["nonce"] == "550e8400-e29b-41d4-a716-446655440000"
    assert (
        decoded_result["hash_fc"]
        == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    )
    data_result: Dict[str, str] = decoded_result["data"]  # pyright: ignore[reportAssignmentType]
    assert data_result["nom_usage"] == "Delaforêt"
    assert data_result["email"] == "wossewodda-37228@yopmail.com"
    assert data_result["commune_nom"] == "Paris"
    assert data_result["commune_cp"] == "75007"
    assert data_result["commune_adresse"] == "20 Avenue de Ségur"
