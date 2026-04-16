import base64
import datetime
from typing import Any, AsyncGenerator, Dict

import jwt
import pytest
from channels.testing.websocket import WebsocketCommunicator
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from webpush.vapid import VAPID

from ami.asgi import application
from ami.notification.models import Notification
from ami.user.models import Registration, User
from ami.user.utils import build_fc_hash


@pytest.fixture(scope="session", autouse=True)
def otv_cert_keys_for_encryption() -> Dict[str, str]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "FR"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
            x509.NameAttribute(NameOID.COMMON_NAME, "test.local"),
        ]
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        .sign(private_key, hashes.SHA256())
    )
    pem_public = cert.public_bytes(serialization.Encoding.PEM).decode()
    pem_private = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    return {"private": pem_private, "public": pem_public}


@pytest.fixture(scope="session", autouse=True)
def otv_cert_keys_for_signature() -> Dict[str, str]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "FR"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
            x509.NameAttribute(NameOID.COMMON_NAME, "test.local"),
        ]
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        .sign(private_key, hashes.SHA256())
    )
    pfx_data = pkcs12.serialize_key_and_certificates(
        name=b"test.local",
        key=private_key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pfx_b64 = base64.b64encode(pfx_data).decode()
    pem_cert = cert.public_bytes(serialization.Encoding.PEM).decode()
    return {
        "pfx_b64": pfx_b64,
        "cert": pem_cert,
    }


@pytest.fixture
def userinfo() -> dict[str, Any]:
    return {
        "sub": "fake sub",
        "given_name": "Angela Claire Louise",
        "given_name_array": ["Angela", "Claire", "Louise"],
        "family_name": "DUBOIS",
        "birthdate": "1962-08-24",
        "birthcountry": "99100",
        "birthplace": "75107",
        "gender": "female",
        "email": "angela@dubois.fr",
        "aud": "fake aud",
        "exp": 1753877658,
        "iat": 1753877598,
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }


@pytest.fixture
def user() -> User:
    fc_hash = build_fc_hash(
        given_name="Test User",
        family_name="AMI",
        birthdate="",
        gender="",
        birthplace="",
        birthcountry="",
    )
    return User.objects.create(
        fc_hash=fc_hash, last_logged_in=datetime.datetime.now(datetime.timezone.utc)
    )


@pytest.fixture
def never_seen_user(user: User) -> User:
    user.last_logged_in = None
    user.save()
    return user


@pytest.fixture(autouse=True)
def patch_webpush(settings) -> None:
    private_key, public_key, _ = VAPID.generate_keys()
    settings.VAPID_PRIVATE_KEY = private_key.decode()
    settings.VAPID_PUBLIC_KEY = public_key.decode()


@pytest.fixture
def webpush_notification(webpush_registration: Registration) -> Notification:
    return Notification.objects.create(
        user_id=webpush_registration.user.id,
        content_body="Hello notification",
        content_title="Notification title",
    )


@pytest.fixture
def webpush_registration(user: User, webpushsubscription: dict[str, Any]) -> Registration:
    return Registration.objects.create(user=user, subscription=webpushsubscription)


@pytest.fixture
async def webpushsubscription() -> dict[str, Any]:
    subscription = {
        "endpoint": "https://example.com/",
        "keys": {
            "auth": "ribfIxhEOtCZ0lkcbB4yCg",
            "p256dh": "BGsTJAJDhGijvPLi0DVPHB86MGLmW1Y6VzjX-FpTlKbhhOtCmU0Vffaj1djCXzR6vkUYrwkOTmh1dgbIQHEyy1k",
        },
    }
    return subscription


@pytest.fixture
async def websocket(user: User, settings) -> AsyncGenerator[WebsocketCommunicator, Any]:
    token = jwt.encode({"sub": str(user.id)}, settings.AUTH_COOKIE_JWT_SECRET, algorithm="HS256")
    headers = [(b"cookie", f"token={token}".encode())]
    communicator = WebsocketCommunicator(
        application, "api/v1/users/notification/events/stream", headers=headers
    )
    await communicator.connect()
    yield communicator
    await communicator.disconnect()


@pytest.fixture(autouse=True)
def use_in_memory_channel_layer(settings) -> None:
    """We don't want django-channels to use the postgresql backend during tests."""
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }


@pytest.fixture
def notification(user: User) -> Notification:
    return Notification.objects.create(
        user_id=user.id,
        content_body="Hello notification",
        content_title="Notification title",
    )


@pytest.fixture
def partner_auth(settings) -> dict[str, str]:
    b64 = base64.b64encode(f"psl:{settings.PARTNERS_PSL_SECRET}".encode("utf8")).decode("utf8")
    return {"authorization": f"Basic {b64}"}


@pytest.fixture
def mobile_notification(mobile_registration: Registration) -> Notification:
    return Notification.objects.create(
        user_id=mobile_registration.user.id,
        content_body="Hello notification",
        content_title="Notification title",
    )


@pytest.fixture
def mobile_registration(user: User, mobileAppSubscription: dict[str, Any]) -> Registration:
    return Registration.objects.create(user_id=user.id, subscription=mobileAppSubscription)


@pytest.fixture
def mobileAppSubscription() -> dict[str, Any]:
    subscription = {
        "app_version": "0.0-local",
        "device_id": "some-id",
        "fcm_token": "some-token",
        "model": "Google sdk_gphone64_arm64",
        "platform": "android",
    }
    return subscription
