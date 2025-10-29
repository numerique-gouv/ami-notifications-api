import json
from collections.abc import Sequence
from typing import Annotated, cast

import httpx
from litestar import Controller, get, patch, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Body
from pydantic import TypeAdapter
from webpush import WebPush, WebPushSubscription

from app import env
from app import models as m
from app import schemas as s
from app.services.notification import NotificationService, provide_notifications_service
from app.services.user import (
    UserService,
    provide_users_service,
    provide_users_with_registrations_service,
)


class NotificationController(Controller):
    dependencies = {
        "notifications_service": Provide(provide_notifications_service),
        "users_service": Provide(provide_users_service),
        "users_with_registrations_service": Provide(provide_users_with_registrations_service),
    }

    @get("/notification-key")
    async def get_notification_key(self) -> str:
        return env.VAPID_APPLICATION_SERVER_KEY

    @post("/api/v1/notifications", return_dto=None)
    async def notify(
        self,
        notifications_service: NotificationService,
        users_with_registrations_service: UserService,
        webpush: WebPush,
        data: Annotated[
            s.NotificationCreate,
            Body(
                title="Send a notification",
                description="Send the notification message to a registered user",
            ),
        ],
    ) -> s.Notification:
        user: m.User | None = await users_with_registrations_service.get_one_or_none(
            id=data.user_id
        )
        if user is None:
            raise NotFoundException(detail="User not found")

        for registration in user.registrations:
            subscription = WebPushSubscription.model_validate(registration.subscription)
            json_data = {"title": data.title, "message": data.message, "sender": data.sender}
            message = webpush.get(message=json.dumps(json_data), subscription=subscription)
            headers = cast(dict[str, str], message.headers)

            response = httpx.post(
                registration.subscription["endpoint"], content=message.encrypted, headers=headers
            )
            if response.status_code < 500:
                # For example we could have "410: gone" if the registration has been revoked.
                continue
            else:
                response.raise_for_status()

        notification: m.Notification = await notifications_service.create(
            m.Notification(**data.model_dump()),
            auto_commit=True,
        )
        return notifications_service.to_schema(notification, schema_type=s.Notification)

    @get("/api/v1/users/{user_id:int}/notifications")
    async def list_notifications(
        self,
        notifications_service: NotificationService,
        users_service: UserService,
        user_id: int,
        unread: bool | None = None,
    ) -> Sequence[s.Notification]:
        user: m.User | None = await users_service.get_one_or_none(id=user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        if unread is not None:
            notifications: Sequence[m.Notification] = await notifications_service.list(
                order_by=(m.Notification.date, True),
                user=user,
                unread=unread,
            )
        else:
            notifications: Sequence[m.Notification] = await notifications_service.list(
                order_by=(m.Notification.date, True),
                user=user,
            )
        # We could do:
        # return notifications_service.to_schema(notifications, schema_type=s.Notification)
        # But it adds pagination.
        # For the moment, just return a list of dict
        type_adapter = TypeAdapter(list[s.Notification])
        return type_adapter.validate_python(notifications)

    @patch("/api/v1/users/{user_id:int}/notification/{notification_id:int}/read")
    async def read_notification(
        self,
        notifications_service: NotificationService,
        users_service: UserService,
        user_id: int,
        notification_id: int,
        data: Annotated[
            s.NotificationRead,
            Body(
                description="Mark a user notification as read or unread",
            ),
        ],
    ) -> s.Notification:
        user: m.User | None = await users_service.get_one_or_none(id=user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        notification: m.Notification | None = await notifications_service.get_one_or_none(
            id=notification_id,
            user=user,
        )
        if notification is None:
            raise NotFoundException(detail="Notification not found")
        notification.unread = not data.read
        notification = await notifications_service.update(
            notification,
            auto_commit=True,
        )
        return notifications_service.to_schema(notification, schema_type=s.Notification)
