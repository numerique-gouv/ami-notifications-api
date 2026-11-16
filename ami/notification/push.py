import logging

from django.conf import settings
from firebase_admin import messaging
from firebase_admin.messaging import UnregisteredError

from ami.notification.models import Notification
from ami.user.models import NotificationPush, Registration
from ami.utils import sentry

logger = logging.getLogger(__name__)


def push(notification: Notification) -> None:
    notification_data = NotificationPush(
        title=notification.content_title,
        message=notification.content_body,
        content_icon=notification.content_icon,
        sender="AMI",
    )
    for registration in Registration.objects.filter(user_id=notification.user_id):
        # We need to make absolutely sure that there are no values that are not strings,
        # or the Firebase admin SDK will fail.
        data = {
            k: str(v)
            for k, v in notification_data.model_dump(mode="json", exclude_none=True).items()
        }
        message = messaging.Message(
            # Send both a Notification (displayed automatically by the operating system)
            # even if the app is in the background...
            notification=messaging.Notification(
                title=notification_data.title,
                body=notification_data.message,
            ),
            # ... and a full data dump, so the app can display more information if needed
            # once the application is displayed.
            data={**data, "app_url": settings.PUBLIC_APP_URL},
            token=registration.typed_subscription.fcm_token,
        )
        try:
            messaging.send(message)
            sentry.add_counter("notification.request.pushed")
        except UnregisteredError:
            logger.warning(
                f"FCM token is invalid or expired for device. Token should be removed: {registration.typed_subscription.fcm_token}"
            )
            # TODO: delete this registration from the database
        except Exception as e:
            logger.exception(f"Failed to send notification: {e}")
