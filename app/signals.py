import json
import uuid
from typing import cast

from advanced_alchemy.extensions.litestar.providers import create_service_provider
from litestar.events import listener
from webpush import WebPushSubscription

from app import models, schemas
from app.database import alchemy_config
from app.httpx import httpxClient
from app.plugins import channels
from app.services.notification import NotificationService
from app.services.registration import RegistrationService
from app.webpush import provide_webpush


@listener("notification_created")
async def create_notification_handler(notification_id: uuid.UUID, try_push: bool) -> None:
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

        channels.publish(  # type: ignore
            {
                "user_id": str(notification.user_id),
                "id": str(notification.id),
                "event": schemas.NotificationEvent.CREATED,
            },
            "notification_events",
        )

        if not try_push:
            return

        webpush = provide_webpush()

        push_data = {
            "title": notification.content_title,
            "message": notification.content_body,
            "sender": notification.sender,
        }
        registrations = await registrations_service.list(user_id=notification.user_id)
        for registration in registrations:
            subscription = WebPushSubscription.model_validate(registration.subscription)
            message = webpush.get(message=json.dumps(push_data), subscription=subscription)
            headers = cast(dict[str, str], message.headers)

            # fail silently
            httpxClient.post(
                registration.subscription["endpoint"], content=message.encrypted, headers=headers
            )
