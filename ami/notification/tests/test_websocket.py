import uuid

import jwt
import pytest
from channels.layers import get_channel_layer
from channels.testing.websocket import WebsocketCommunicator
from django.conf import settings

from ami.asgi import application
from ami.user.models import User


@pytest.mark.django_db(transaction=True)
async def test_stream_notification_events(
    websocket: WebsocketCommunicator,
    user: User,
) -> None:
    channel_layer = get_channel_layer()
    assert channel_layer is not None

    # Publish to a different user's group: should not be received
    await channel_layer.group_send(
        f"user_{uuid.uuid4()}",
        {
            "type": "notification.event",
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "event": "foo-event",
        },
    )

    # Publish to the authenticated user's group: should be received
    expected = {
        "id": str(uuid.uuid4()),
        "user_id": str(user.id),
        "event": "foo-event",
    }
    await channel_layer.group_send(
        f"user_{user.id}",
        {"type": "notification.event", **expected},
    )

    message = await websocket.receive_json_from(timeout=1)
    assert message == expected


@pytest.mark.django_db(transaction=True)
async def test_stream_notification_events_without_auth() -> None:
    communicator = WebsocketCommunicator(application, "api/v1/users/notification/events/stream")
    connected, code = await communicator.connect()
    assert not connected
    assert code == settings.PUBLIC_CHANNEL_UNAUTHORIZED_CODE

    token = jwt.encode({"sub": "bad-value"}, "wrong-secret", algorithm="HS256")
    headers = [(b"cookie", f"{settings.AUTH_COOKIE_JWT_NAME}=Bearer {token}".encode())]
    communicator = WebsocketCommunicator(
        application, "api/v1/users/notification/events/stream", headers=headers
    )
    connected, code = await communicator.connect()
    assert not connected
    assert code == settings.PUBLIC_CHANNEL_UNAUTHORIZED_CODE
