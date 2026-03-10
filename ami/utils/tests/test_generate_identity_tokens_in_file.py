import csv
import datetime
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

import pytest
from django.core.management import call_command
from freezegun import freeze_time
from freezegun.api import FakeDatetime

from ami.utils import decode_identity_token, decrypt_data, generate_identity_token


@freeze_time("2026-01-23 10:36:00")
def test_cli_generate_identity_tokens(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    csv_content = (
        "id,fc_hash,preferred_username,email,address_city,address_postcode,address_name\n"
        "1,4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060,,"
        "wossewodda-3728@yopmail.com,Paris,75007,20 Avenue de Ségur\n"
    )
    input_csv_file_path = tmp_path / "input_file_test_cli.csv"
    input_csv_file_path.write_text(csv_content, encoding="utf-8")
    output_csv_file_path = tmp_path / "output_file_test_cli.csv"
    output_csv_file_path.write_text("", encoding="utf-8")

    def mock_generate_identity_token(**kwargs: Any):
        return "fake-identity-token"

    monkeypatch.setattr(
        "ami.utils.generate_identity_token",
        mock_generate_identity_token,
    )

    call_command("generate-identity-tokens", str(input_csv_file_path), str(output_csv_file_path))

    input_fieldnames = [
        "id",
        "preferred_username",
        "email",
        "address_city",
        "address_postcode",
        "address_name",
        "fc_hash",
    ]
    output_fieldnames = input_fieldnames + ["identity_token"]

    input_data = get_data_from_file(str(tmp_path / "input_file_test_cli.csv"), input_fieldnames)
    output_data = get_data_from_file(str(tmp_path / "output_file_test_cli.csv"), output_fieldnames)

    assert input_data[0]["id"] == output_data[0]["id"]
    assert input_data[0]["preferred_username"] == output_data[0]["preferred_username"]
    assert input_data[0]["email"] == output_data[0]["email"]
    assert input_data[0]["address_city"] == output_data[0]["address_city"]
    assert input_data[0]["address_postcode"] == output_data[0]["address_postcode"]
    assert input_data[0]["address_name"] == output_data[0]["address_name"]
    assert input_data[0]["fc_hash"] == output_data[0]["fc_hash"]
    assert output_data[0]["identity_token"] is not None


def get_data_from_file(
    file_path: str,
    fieldnames: List[str],
) -> List[Any]:
    results: List[Dict[str, str]] = []

    with open(file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row in csv_reader:
            new_line: Dict[str, str] = {}
            for fieldname in fieldnames:
                new_line[fieldname] = row[fieldname]

            results.append(new_line)

    return results


@freeze_time("2026-01-23 10:36:00")
def test_generate_identity_token(
    monkeypatch: pytest.MonkeyPatch,
    settings,
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

    partners_psl_otv_jwt_private_key = "fake-private-key"
    partners_psl_otv_jwe_public_key = "fake-public-key"
    expected_token = "fake-generated-identity-token"
    encrypted_data = "fake-encrypted-data"

    def mock_encrypt_data(*args: Any):
        return encrypted_data

    def mock_get_partners_psl_otv_jwt_private_key(*args: Any):
        return partners_psl_otv_jwt_private_key

    def mock_jwt_encode(payload: Any, key: Any, **kwargs: Any) -> str:
        assert payload["iss"] == "ami"
        assert payload["iat"] == 1769164560
        assert payload["exp"] == FakeDatetime(2026, 1, 23, 11, 6, tzinfo=datetime.timezone.utc)
        assert payload["nonce"] == mock_uuid_str
        assert payload["hash_fc"] == fc_hash
        assert payload["data"] == encrypted_data
        assert key == partners_psl_otv_jwt_private_key
        assert kwargs["algorithm"] == "RS256"
        return expected_token

    settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"] = partners_psl_otv_jwe_public_key
    monkeypatch.setattr("ami.utils.encrypt_data", mock_encrypt_data)
    monkeypatch.setattr("ami.utils.uuid4", mock_uuid_uuid4)
    monkeypatch.setattr(
        "ami.utils.get_partners_psl_otv_jwt_private_key", mock_get_partners_psl_otv_jwt_private_key
    )
    monkeypatch.setattr("jwt.encode", mock_jwt_encode)

    # When
    token = generate_identity_token(
        preferred_username, email, address_city, address_postcode, address_name, fc_hash
    )

    # Then
    assert token == expected_token


@freeze_time("2026-01-23 10:36:00")
def test_generate_identity_token_with_decode(
    monkeypatch: pytest.MonkeyPatch,
    settings,
    otv_cert_keys_for_encryption: Dict[str, str],
    otv_cert_keys_for_signature: Dict[str, str],
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

    monkeypatch.setattr("ami.utils.uuid4", mock_uuid_uuid4)

    fake_private_key_for_encryption: str = otv_cert_keys_for_encryption["private"]
    fake_public_key_for_encryption: str = otv_cert_keys_for_encryption["public"]
    fake_private_key_for_signature: str = otv_cert_keys_for_signature["pfx_b64"]
    fake_public_key_for_signature: str = otv_cert_keys_for_signature["cert"]

    settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"] = fake_public_key_for_encryption
    monkeypatch.setattr("ami.utils.uuid4", mock_uuid_uuid4)
    settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PFX_B64"] = fake_private_key_for_signature
    settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PUBLIC_KEY"] = fake_public_key_for_signature

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
    data_encrypted = decoded_result["data"]
    data_result = decrypt_data(data_encrypted, fake_private_key_for_encryption)
    assert data_result["nom_usage"] == "Delaforêt"
    assert data_result["email"] == "wossewodda-37228@yopmail.com"
    assert data_result["commune_nom"] == "Paris"
    assert data_result["commune_cp"] == "75007"
    assert data_result["commune_adresse"] == "20 Avenue de Ségur"
