import base64
import csv
import datetime
import gzip
import json
from typing import Dict, Union
from uuid import uuid4

import jwt
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import pkcs12
from django.conf import settings


def encrypt_data(data: dict[str, str], public_key: str) -> str:
    key = x509.load_pem_x509_certificate(public_key.encode()).public_key()
    if not isinstance(key, RSAPublicKey):
        raise ValueError("Expected RSA public key")
    rsa_public_key = key  # narrowed to RSAPublicKey

    encrypted = rsa_public_key.encrypt(
        gzip.compress(json.dumps(data).encode()),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )
    return base64.b64encode(encrypted).decode()


def decrypt_data(data: str, private_key: str) -> dict[str, str]:
    key = serialization.load_pem_private_key(private_key.encode(), password=None)
    if not isinstance(key, RSAPrivateKey):
        raise ValueError("Expected RSA private key")
    rsa_private_key = key  # narrowed to RSAPrivateKey

    decrypted = rsa_private_key.decrypt(
        base64.b64decode(data),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )
    return json.loads(gzip.decompress(decrypted).decode())


def get_partners_psl_otv_jwt_private_key() -> RSAPrivateKey:
    pfx_b64 = settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PFX_B64"]
    pfx_data = base64.b64decode(pfx_b64)
    private_key, _, _ = pkcs12.load_key_and_certificates(pfx_data, None)

    if not isinstance(private_key, RSAPrivateKey):
        raise ValueError("Expected RSA private key")
    rsa_private_key = private_key  # narrowed to RSAPrivateKey

    return rsa_private_key


def sign_identity_token(payload: Dict[str, Union[str, int, datetime.datetime]]) -> str:
    private_key = get_partners_psl_otv_jwt_private_key()
    return jwt.encode(payload, private_key, algorithm="RS256")


def generate_identity_token(
    preferred_username: str,
    email: str,
    address_city: str,
    address_postcode: str,
    address_name: str,
    fc_hash: str,
) -> str:
    data = {
        "nom_usage": preferred_username,
        "email": email,
        "commune_nom": address_city,
        "commune_cp": address_postcode,
        "commune_adresse": address_name,
    }
    data_encrypted = encrypt_data(data, settings.CONFIG["PARTNERS_PSL_OTV_JWE_PUBLIC_KEY"])
    payload = {
        "iss": "ami",
        "iat": int(datetime.datetime.now().timestamp()),
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30),
        "nonce": str(uuid4()),
        "hash_fc": fc_hash,
        "data": data_encrypted,
    }

    return sign_identity_token(payload)


def decode_identity_token(token: str) -> dict[str, str]:
    cert_pem = settings.CONFIG["PARTNERS_PSL_OTV_JWT_CERT_PUBLIC_KEY"].encode()
    cert = x509.load_pem_x509_certificate(cert_pem, default_backend())
    public_key_pem = (
        cert.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    return jwt.decode(token, public_key_pem.encode(), algorithms=["RS256"])


def generate_identity_tokens_in_file(
    input_file_path: str,
    output_file_path: str,
) -> None:
    results = []

    with open(input_file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row in csv_reader:
            preferred_username = row["preferred_username"]
            email = row["email"]
            address_city = row["address_city"]
            address_postcode = row["address_postcode"]
            address_name = row["address_name"]
            fc_hash = row["fc_hash"]
            response = generate_identity_token(
                preferred_username=preferred_username,
                email=email,
                address_city=address_city,
                address_postcode=address_postcode,
                address_name=address_name,
                fc_hash=fc_hash,
            )

            results.append(  # type: ignore[reportUnknownMemberType]
                {
                    "id": row["id"],
                    "preferred_username": row["preferred_username"],
                    "email": row["email"],
                    "address_city": row["address_city"],
                    "address_postcode": row["address_postcode"],
                    "address_name": row["address_name"],
                    "fc_hash": row["fc_hash"],
                    "identity_token": response,
                }
            )

    with open(output_file_path, "w") as csv_file:
        fieldnames = [
            "id",
            "preferred_username",
            "email",
            "address_city",
            "address_postcode",
            "address_name",
            "fc_hash",
            "identity_token",
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in results:  # type: ignore[reportUnknownVariableType]
            writer.writerow(
                {
                    "id": row["id"],
                    "preferred_username": row["preferred_username"],
                    "email": row["email"],
                    "address_city": row["address_city"],
                    "address_postcode": row["address_postcode"],
                    "address_name": row["address_name"],
                    "fc_hash": row["fc_hash"],
                    "identity_token": row["identity_token"],
                }
            )
