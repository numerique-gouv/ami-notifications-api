from channels.layers import get_channel_layer
from django.conf import settings
from webpush import WebPush

from ami.notification.models import Notification, NotificationEvent


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=settings.CONFIG["VAPID_PUBLIC_KEY"].encode(),
        private_key=settings.CONFIG["VAPID_PRIVATE_KEY"].encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush


async def push(notification: Notification, try_push: bool) -> None:
    # TODO: implement the push notification mechanism
    channel_layer = get_channel_layer()
    assert channel_layer is not None
    await channel_layer.group_send(
        f"user_{notification.user.id}",
        {
            "type": "notification.event",  # maps to notification_event() on the consumer
            "user_id": str(notification.user.id),
            "id": str(notification.id),
            "event": NotificationEvent.CREATED,
        },
    )
