import json
import uuid
from collections.abc import Sequence
from typing import Annotated, Any, cast

from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Response, WebSocket, get, patch, post, websocket
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.exceptions import (
    NotFoundException,
    WebSocketDisconnect,
)
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK
from pydantic import TypeAdapter
from webpush import WebPush, WebPushSubscription

from app import env, models, schemas
from app.httpx import httpxClient
from app.schemas import NotifyResponse
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
        unread: bool | None = None,
    ) -> Sequence[schemas.AdminNotification]:
        if unread is not None:
            notifications: Sequence[models.Notification] = await notifications_service.list(
                order_by=(models.Notification.created_at, True),
                user=current_user,
                unread=unread,
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
        type_adapter = TypeAdapter(list[schemas.AdminNotification])
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
    ) -> schemas.AdminNotification:
        notification: models.Notification | None = await notifications_service.get_one_or_none(
            id=notification_id,
            user=current_user,
        )
        if notification is None:
            raise NotFoundException(detail="Notification not found")
        notification.unread = not data.read
        notification = await notifications_service.update(notification)
        channels.publish(  # type: ignore
            {
                "user_id": str(current_user.id),
                "id": str(notification.id),
                "event": schemas.NotificationEvent.UPDATED,
            },
            "notification_events",
        )
        return notifications_service.to_schema(notification, schema_type=schemas.AdminNotification)

    @websocket("/api/v1/users/notification/events/stream")
    async def stream_notification_events(
        self,
        socket: WebSocket[Any, Any, Any],
        channels: ChannelsPlugin,
        current_user: models.User,
    ) -> None:
        async def _sender(message: str) -> None:
            data = json.loads(message)
            if data["user_id"] != str(current_user.id):
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


class NotAuthenticatedNotificationController(Controller):
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
    async def admin_notify(
        self,
        channels: ChannelsPlugin,
        notifications_service: NotificationService,
        users_with_registrations_service: UserService,
        webpush: WebPush,
        data: schemas.NotificationCreate,
    ) -> schemas.AdminNotification:
        user: models.User | None = await users_with_registrations_service.get_one_or_none(
            id=data.user_id
        )
        if user is None:
            raise NotFoundException(detail="User not found")

        for registration in user.registrations:
            subscription = WebPushSubscription.model_validate(registration.subscription)
            json_data = {"title": data.title, "message": data.message, "sender": data.sender}
            message = webpush.get(message=json.dumps(json_data), subscription=subscription)
            headers = cast(dict[str, str], message.headers)

            response = httpxClient.post(
                registration.subscription["endpoint"], content=message.encrypted, headers=headers
            )
            if response.status_code < 500:
                # For example we could have "410: gone" if the registration has been revoked.
                continue
            else:
                response.raise_for_status()

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
        return notifications_service.to_schema(notification, schema_type=schemas.AdminNotification)

    @get("/api/v1/users/{user_id:uuid}/notifications")
    async def list_notifications(
        self,
        notifications_service: NotificationService,
        users_service: UserService,
        user_id: uuid.UUID,
        unread: bool | None = None,
    ) -> Sequence[schemas.AdminNotification]:
        # XXX keep this endpoint for mobile-app compatibility; remove it when mobile-app use authenticated endpoint
        user: models.User | None = await users_service.get_one_or_none(id=user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        if unread is not None:
            notifications: Sequence[models.Notification] = await notifications_service.list(
                order_by=(models.Notification.created_at, True),
                user=user,
                unread=unread,
            )
        else:
            notifications: Sequence[models.Notification] = await notifications_service.list(
                order_by=(models.Notification.created_at, True),
                user=user,
            )
        # We could do:
        # return notifications_service.to_schema(notifications, schema_type=schemas.Notification)
        # But it adds pagination.
        # For the moment, just return a list of dict
        type_adapter = TypeAdapter(list[schemas.AdminNotification])
        return type_adapter.validate_python(notifications)

    @post("/api/v1/notifications")
    async def notify(
        self,
        data: Annotated[
            schemas.Notification,
            Body(
                title="Send a notification",
                description="Send the notification message to a registered user",
            ),
        ],
    ) -> Response[NotifyResponse]:
        notification_id = uuid.UUID("43847a2f-0b26-40a4-a452-8342a99a10a8")
        status_code = HTTP_200_OK
        notification_send_status = True

        if data.recipient_fc_hash == "unknown_hash":
            notification_send_status = False
        elif data.recipient_fc_hash == "technical_error":
            print(0 / 0)

        notify_response = NotifyResponse.model_validate(
            {
                "notification_id": notification_id,
                "notification_send_status": notification_send_status,
            }
        )
        return Response(
            status_code=status_code,
            content=notify_response,
        )
