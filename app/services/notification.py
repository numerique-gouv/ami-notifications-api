import uuid
from typing import cast

from advanced_alchemy.extensions.litestar import repository, service
from advanced_alchemy.extensions.litestar.providers import create_service_provider
from firebase_admin import messaging
from firebase_admin.messaging import UnregisteredError
from litestar.channels import ChannelsPlugin
from webpush import WebPush, WebPushSubscription

from app import models, schemas
from app.database import alchemy_config
from app.httpx import httpxClient
from app.services.registration import RegistrationService


class NotificationService(service.SQLAlchemyAsyncRepositoryService[models.Notification]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.Notification]):
        model_type = models.Notification

    repository_type = Repo

    @staticmethod
    async def push_notification(
        channels: ChannelsPlugin,
        webpush: WebPush,
        notification_id: uuid.UUID,
        try_push: bool,
    ) -> None:
        import logging

        logger = logging.getLogger(__name__)

        provide_notifications_service = create_service_provider(NotificationService)
        provide_registrations_service = create_service_provider(RegistrationService)
        async with alchemy_config.get_session() as db_session:
            notifications_service: NotificationService = await anext(
                provide_notifications_service(db_session)
            )
            registrations_service: RegistrationService = await anext(
                provide_registrations_service(db_session)
            )

            notification: models.Notification | None = await notifications_service.get_one_or_none(
                id=notification_id
            )
            if notification is None:
                return

            await channels.wait_published(  # type: ignore
                {
                    "user_id": str(notification.user_id),
                    "id": str(notification.id),
                    "event": schemas.NotificationEvent.CREATED,
                },
                "notification_events",
            )

            if not try_push:
                return

            notification_data = schemas.NotificationPush(
                content_title=notification.content_title,
                content_body=notification.content_body,
                content_icon=notification.content_icon,
                sender=notification.sender,
            )
            registrations = await registrations_service.list(user_id=notification.user_id)
            for registration in registrations:
                if isinstance(registration.typed_subscription, schemas.WebPushSubscription):
                    subscription = WebPushSubscription.model_validate(
                        registration.typed_subscription
                    )
                    message = webpush.get(
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
                            title=notification_data.content_title,
                            body=notification_data.content_body,
                        ),
                        # ... and a full data dump, so the app can display more information if needed
                        # once the application is displayed.
                        # We need to make absolutely sure that there are no values that are not strings,
                        # or the Firebase admin SDK will fail.
                        data={
                            k: str(v)
                            for k, v in notification_data.model_dump(
                                mode="json", exclude_none=True
                            ).items()
                        },
                        token=registration.typed_subscription.fcm_token,
                    )
                    try:
                        response = messaging.send(message)

                    except UnregisteredError:
                        logger.warning(
                            f"FCM token is invalid or expired for device. Token should be removed: {registration.typed_subscription.fcm_token}"
                        )
                        # TODO: delete this registration from the database
                    except Exception as e:
                        logger.exception(f"Failed to send notification: {e}")
