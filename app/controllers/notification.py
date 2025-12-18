import json
import uuid
from collections.abc import Sequence
from typing import Annotated, Any, cast

from advanced_alchemy.extensions.litestar import providers
from firebase_admin import messaging
from firebase_admin.messaging import UnregisteredError
from litestar import Controller, Response, WebSocket, get, patch, post, websocket
from litestar.background_tasks import BackgroundTask
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.exceptions import (
    NotFoundException,
    WebSocketDisconnect,
)
from litestar.params import Body
from pydantic import TypeAdapter
from webpush import WebPush, WebPushSubscription

from app import env, models, schemas
from app.httpx import httpxClient
from app.partners import Partner, provide_partner
from app.services.notification import NotificationService
from app.services.user import UserService, provide_user


class NotificationController(Controller):
    dependencies = {
        "current_user": Provide(provide_user),
        "notifications_service": providers.create_service_provider(NotificationService),
    }

    @get("/api/v1/users/notifications")
    async def list_notifications(
        self,
        notifications_service: NotificationService,
        current_user: models.User,
        read: bool | None = None,
    ) -> Sequence[schemas.Notification]:
        if read is not None:
            notifications: Sequence[models.Notification] = await notifications_service.list(
                order_by=(models.Notification.created_at, True),
                user=current_user,
                read=read,
            )
        else:
            notifications: Sequence[models.Notification] = await notifications_service.list(
                order_by=(models.Notification.created_at, True),
                user=current_user,
            )
        # We could do:
        # return notifications_service.to_schema(notifications, schema_type=schemas.Notification)
        # But it adds pagination.
        # For the moment, just return a list of dict
        type_adapter = TypeAdapter(list[schemas.Notification])
        return type_adapter.validate_python(notifications)

    @patch("/api/v1/users/notification/{notification_id:uuid}/read")
    async def read_notification(
        self,
        channels: ChannelsPlugin,
        notifications_service: NotificationService,
        current_user: models.User,
        notification_id: uuid.UUID,
        data: Annotated[
            schemas.NotificationRead,
            Body(
                description="Mark a user notification as read or unread",
            ),
        ],
    ) -> schemas.Notification:
        notification: models.Notification | None = await notifications_service.get_one_or_none(
            id=notification_id,
            user=current_user,
        )
        if notification is None:
            raise NotFoundException(detail="Notification not found")
        notification.read = data.read
        notification = await notifications_service.update(notification)
        channels.publish(  # type: ignore
            {
                "user_id": str(current_user.id),
                "id": str(notification.id),
                "event": schemas.NotificationEvent.UPDATED,
            },
            "notification_events",
        )
        return notifications_service.to_schema(notification, schema_type=schemas.Notification)

    @websocket("/api/v1/users/notification/events/stream")
    async def stream_notification_events(
        self,
        socket: WebSocket[Any, Any, Any],
        channels: ChannelsPlugin,
        current_user: models.User,
    ) -> None:
        # Extract user_id immediately and don't hold reference to User object
        # to avoid keeping database session open for the lifetime of the WebSocket
        user_id = str(current_user.id)

        async def _sender(message: str) -> None:
            data = json.loads(message)
            if data["user_id"] != user_id:
                return
            await socket.send_json(data)

        await socket.accept()

        # then listen for notification events
        async with (
            channels.start_subscription(["notification_events"]) as subscriber,
            subscriber.run_in_background(_sender),  # type:ignore
        ):
            while True:
                try:
                    message = await socket.receive_text()
                    if message == "close":
                        # XXX this is for tests
                        await socket.close()
                        return
                except WebSocketDisconnect:
                    # if the socket is closed, avoid exception trace
                    return


class PushNotificationMixin:
    def _push_notification(
        self,
        webpush: WebPush,
        subscriptions: list[WebPushSubscription | schemas.MobileAppSubscription],
        notification_data: schemas.NotificationPush,
    ) -> None:
        """Push notifications to external endpoints. Runs as a background task."""
        import logging

        logger = logging.getLogger(__name__)

        for subscription in subscriptions:
            if isinstance(subscription, WebPushSubscription):
                message = webpush.get(
                    message=notification_data.model_dump_json(), subscription=subscription
                )
                headers = cast(dict[str, str], message.headers)

                response = httpxClient.post(
                    str(subscription.endpoint), content=message.encrypted, headers=headers
                )
                if response.status_code < 500:
                    # For example we could have "410: gone" if the registration has been revoked.
                    # TODO: delete this registration from the database
                    continue
                else:
                    response.raise_for_status()
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
                    token=subscription.fcm_token,
                )
                try:
                    response = messaging.send(message)

                except UnregisteredError:
                    logger.warning(
                        f"FCM token is invalid or expired for device. Token should be removed: {subscription.fcm_token}"
                    )
                    # TODO: delete this registration from the database
                except Exception as e:
                    logger.exception(f"Failed to send notification: {e}")
                    # Continue to next subscription instead of failing completely
                    continue


class NotAuthenticatedNotificationController(PushNotificationMixin, Controller):
    dependencies = {
        "notifications_service": providers.create_service_provider(NotificationService),
        "users_service": providers.create_service_provider(UserService),
        "users_with_registrations_service": providers.create_service_provider(
            UserService, load=[models.User.registrations]
        ),
    }

    @get("/notification-key")
    async def get_notification_key(self) -> str:
        return env.VAPID_APPLICATION_SERVER_KEY

    @post("/ami_admin/notifications", include_in_schema=False)
    async def admin_create_notification(
        self,
        channels: ChannelsPlugin,
        notifications_service: NotificationService,
        users_with_registrations_service: UserService,
        webpush: WebPush,
        data: schemas.AdminNotificationCreate,
    ) -> Response[schemas.NotificationResponse]:
        user: models.User | None = await users_with_registrations_service.get_one_or_none(
            id=data.user_id
        )
        if user is None:
            raise NotFoundException(detail="User not found")

        # Extract subscription data before creating notification to avoid holding DB session
        subscriptions = [reg.typed_subscription for reg in user.registrations]
        push_data = schemas.NotificationPush(
            content_title=data.content_title,
            content_body=data.content_body,
            content_icon="fr-icon-mail-star-line",
            sender=data.sender,
        )

        notification: models.Notification = await notifications_service.create(
            models.Notification(**data.model_dump())
        )
        channels.publish(  # type: ignore
            {
                "user_id": str(user.id),
                "id": str(notification.id),
                "event": schemas.NotificationEvent.CREATED,
            },
            "notification_events",
        )

        # Push notifications in background after DB transaction completes
        background_task = BackgroundTask(
            self._push_notification,
            webpush=webpush,
            subscriptions=subscriptions,
            notification_data=push_data,
        )

        response_data = schemas.NotificationResponse.model_validate(
            {
                "notification_id": notification.id,
                "notification_send_status": True,
            }
        )
        return Response(content=response_data, background=background_task)

    @get("/api/v1/users/{user_id:uuid}/notifications", include_in_schema=False)
    async def list_notifications(
        self,
        notifications_service: NotificationService,
        users_service: UserService,
        user_id: uuid.UUID,
        read: bool | None = None,
    ) -> Sequence[schemas.NotificationLegacy]:
        # XXX keep this endpoint for mobile-app compatibility; remove it when mobile-app use authenticated endpoint
        user: models.User | None = await users_service.get_one_or_none(id=user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        if read is not None:
            notifications: Sequence[models.Notification] = await notifications_service.list(
                order_by=(models.Notification.created_at, True),
                user=user,
                read=read,
            )
        else:
            notifications: Sequence[models.Notification] = await notifications_service.list(
                order_by=(models.Notification.created_at, True),
                user=user,
            )
        # We could do:
        # return notifications_service.to_schema(notifications, schema_type=schemas.NotificationLegacy)
        # But it adds pagination.
        # For the moment, just return a list of dict
        type_adapter = TypeAdapter(list[schemas.NotificationLegacy])
        return type_adapter.validate_python(notifications)


class PartnerNotificationController(PushNotificationMixin, Controller):
    dependencies = {
        "current_partner": Provide(provide_partner),
        "notifications_service": providers.create_service_provider(NotificationService),
        "users_with_registrations_service": providers.create_service_provider(
            UserService, load=[models.User.registrations]
        ),
    }

    @post("/api/v1/notifications")
    async def create_notification(
        self,
        channels: ChannelsPlugin,
        notifications_service: NotificationService,
        users_with_registrations_service: UserService,
        webpush: WebPush,
        data: Annotated[
            schemas.NotificationCreate,
            Body(
                title="Send a notification",
                description="Send the notification message to a registered user",
            ),
        ],
        current_partner: Partner,
    ) -> Response[schemas.NotificationResponse]:
        notification_send_status = True

        user: models.User | None = await users_with_registrations_service.get_one_or_none(
            fc_hash=data.recipient_fc_hash
        )
        subscriptions: list[WebPushSubscription | schemas.MobileAppSubscription] = []
        if user is None:
            user = await users_with_registrations_service.create(
                models.User(fc_hash=data.recipient_fc_hash, already_seen=False)
            )
            notification_send_status = False
        else:
            # Extract subscription data before creating notification to avoid holding DB session
            subscriptions = [reg.typed_subscription for reg in user.registrations]
            notification_send_status = user.already_seen

        if not data.try_push or not user.already_seen:
            # don't push notification if not required or if user has never logged in on AMI
            subscriptions = []

        notification_data = data.model_dump()
        notification_data.pop("recipient_fc_hash")
        notification_data.pop("try_push")
        if notification_data["content_icon"] is None:
            notification_data["content_icon"] = current_partner.icon or "fr-icon-mail-star-line"
        notification_data["sender"] = current_partner.name
        notification: models.Notification = await notifications_service.create(
            models.Notification(user_id=user.id, **notification_data)
        )
        channels.publish(  # type: ignore
            {
                "user_id": str(user.id),
                "id": str(notification.id),
                "event": schemas.NotificationEvent.CREATED,
            },
            "notification_events",
        )

        # Push notifications in background after DB transaction completes
        push_data = schemas.NotificationPush(
            content_title=notification_data["content_title"],
            content_body=notification_data["content_body"],
            content_icon=notification_data["content_icon"],
            sender=notification_data["sender"],
        )

        background_task = BackgroundTask(
            self._push_notification,
            webpush=webpush,
            subscriptions=subscriptions,
            notification_data=push_data,
        )

        response_data = schemas.NotificationResponse.model_validate(
            {
                "notification_id": notification.id,
                "notification_send_status": notification_send_status,
            }
        )
        return Response(content=response_data, background=background_task)
