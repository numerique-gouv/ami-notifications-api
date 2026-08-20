import base64
import gzip
import json
import os
import random
import string
from typing import Dict

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ami.utils import encrypt_data


@pytest.mark.skip()
def test_encrypt_data_length(
    otv_cert_keys_for_encryption: Dict[str, str],
) -> None:
    fake_public_key_for_encryption: str = otv_cert_keys_for_encryption["public"]

    for i in range(8):
        data = ""
        for j in range(10**i):
            data += random.choice(string.ascii_letters)  # plante entre 100 et 1000 caractères
            # data += 'x'  # plante entre 100 000 et 1 000 000 caractères
        print(i, len(data))
        # ValueError: Encryption failed ?
        result = encrypt_data({"foo": data}, fake_public_key_for_encryption)
        print(len(result))  # toujours 344 caractères


# limite GET param: 2048 caractères
# limite POST: illimité en théorie, en pratique limité par les serveur web pour limiter la taille des fichiers uploadés; par exemple 10 Mo.


JWE_HEADER = {
    "alg": "RSA-OAEP-256",
    "enc": "A256GCM",
    "typ": "JWE",
}


def encrypt_aes_data(data: dict[str, str], public_key: str) -> str:
    key = x509.load_pem_x509_certificate(public_key.encode()).public_key()
    if not isinstance(key, RSAPublicKey):
        raise ValueError("Expected RSA public key")
    rsa_public_key = key  # narrowed to RSAPublicKey

    # random AES-256 key (CEK = Content Encryption Key)
    cek = os.urandom(32)

    # encrypt key
    encrypted_cek = rsa_public_key.encrypt(
        cek,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )

    # serialize JWE header
    header_b64 = base64.b64encode(json.dumps(JWE_HEADER, separators=(",", ":")).encode()).decode()

    # encrypt payload with AES-256-GCM
    iv = os.urandom(12)  # 96 bits
    aesgcm = AESGCM(cek)
    plaintext = gzip.compress(json.dumps(data).encode())
    ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, header_b64.encode())

    # split ciphertext and tag
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]

    return ".".join(
        [
            header_b64,
            base64.b64encode(encrypted_cek).decode(),
            base64.b64encode(iv).decode(),
            base64.b64encode(ciphertext).decode(),
            base64.b64encode(tag).decode(),
        ]
    )


def decrypt_aes_data(data: str, private_key: str) -> dict[str, str]:
    key = serialization.load_pem_private_key(private_key.encode(), password=None)
    if not isinstance(key, RSAPrivateKey):
        raise ValueError("Expected RSA private key")
    rsa_private_key = key  # narrowed to RSAPrivateKey

    header_b64, enc_cek_b64, iv_b64, ciphertext_b64, tag_b64 = data.split(".")

    # decrypt cek
    cek = rsa_private_key.decrypt(
        base64.b64decode(enc_cek_b64),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )

    # decrypt AES-256-GCM payload
    iv = base64.b64decode(iv_b64)
    ciphertext = base64.b64decode(ciphertext_b64)
    tag = base64.b64decode(tag_b64)
    aesgcm = AESGCM(cek)
    plaintext = aesgcm.decrypt(iv, ciphertext + tag, header_b64.encode())

    return json.loads(gzip.decompress(plaintext).decode())

    decrypted = rsa_private_key.decrypt(
        base64.b64decode(data),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ),
    )
    return json.loads(gzip.decompress(decrypted).decode())


def test_encrypt_data_with_aes_length(
    otv_cert_keys_for_encryption: Dict[str, str],
) -> None:
    fake_private_key_for_encryption: str = otv_cert_keys_for_encryption["private"]
    fake_public_key_for_encryption: str = otv_cert_keys_for_encryption["public"]

    for i in range(8):
        data = ""
        for j in range(10**i):
            data += random.choice(string.ascii_letters)
        print(i, len(data))
        result = encrypt_aes_data({"foo": data}, fake_public_key_for_encryption)
        print(
            len(result)
        )  # non fixe, augmente avec la taille de data (97 108 572 caractères pour 100 000 000 caractères encryptés)

        decrypted_result = decrypt_aes_data(result, fake_private_key_for_encryption)
        assert decrypted_result == {"foo": data}
