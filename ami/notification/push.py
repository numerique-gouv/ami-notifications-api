from typing import cast

import webpush
from channels.layers import get_channel_layer
from django.conf import settings
from firebase_admin import messaging
from firebase_admin.messaging import UnregisteredError

from ami.notification.models import Notification, NotificationEvent
from ami.user.models import NotificationPush, Registration, WebPushSubscription
from ami.utils import sentry
from ami.utils.httpx import httpxClient


def provide_webpush() -> webpush.WebPush:
    webpush_ = webpush.WebPush(
        public_key=settings.CONFIG.get("VAPID_PUBLIC_KEY", "").encode(),
        private_key=settings.CONFIG.get("VAPID_PRIVATE_KEY", "").encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush_


async def push(notification: Notification, try_push: bool) -> None:
    import logging

    logger = logging.getLogger(__name__)

    channel_layer = get_channel_layer()
    assert channel_layer is not None
    await channel_layer.group_send(
        f"user_{notification.user_id}",
        {
            "type": "notification.event",  # maps to notification_event() on the consumer
            "user_id": str(notification.user_id),
            "id": str(notification.id),
            "event": NotificationEvent.CREATED,
        },
    )

    if not try_push:
        return

    notification_data = NotificationPush(
        title=notification.content_title,
        message=notification.content_body,
        content_icon=notification.content_icon,
        sender=notification.sender,
    )
    registrations = [r async for r in Registration.objects.filter(user_id=notification.user_id)]
    for registration in registrations:
        if isinstance(registration.typed_subscription, WebPushSubscription):
            subscription = registration.typed_subscription
            message = provide_webpush().get(
                message=notification_data.model_dump_json(), subscription=subscription
            )
            headers = cast(dict[str, str], message.headers)

            # fail silently
            response = httpxClient.post(
                str(subscription.endpoint), content=message.encrypted, headers=headers
            )
            if response.status_code < 500:
                # For example we could have "410: gone" if the registration has been revoked.
                # TODO: delete this registration from the database
                logger.warning("Subscription is 'gone', obsolete, and should be removed")
            else:
                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.exception(f"Failed to send notification: {e}")
        else:
            message = messaging.Message(
                # Send both a Notification (displayed automatically by the operating system)
                # even if the app is in the background...
                notification=messaging.Notification(
                    title=notification_data.title,
                    body=notification_data.message,
                ),
                # ... and a full data dump, so the app can display more information if needed
                # once the application is displayed.
                # We need to make absolutely sure that there are no values that are not strings,
                # or the Firebase admin SDK will fail.
                data={
                    k: str(v)
                    for k, v in notification_data.model_dump(mode="json", exclude_none=True).items()
                },
                token=registration.typed_subscription.fcm_token,
            )
            try:
                response = messaging.send(message)
                sentry.add_counter("notification.request.pushed")
            except UnregisteredError:
                logger.warning(
                    f"FCM token is invalid or expired for device. Token should be removed: {registration.typed_subscription.fcm_token}"
                )
                # TODO: delete this registration from the database
            except Exception as e:
                logger.exception(f"Failed to send notification: {e}")
