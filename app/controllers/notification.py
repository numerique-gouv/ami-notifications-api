import json
from typing import Annotated, cast

import httpx
from litestar import Controller, get, patch, post
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Body
from webpush import WebPush, WebPushSubscription

from app import env
from app import models as m
from app import schemas as s
from app.repositories.notification import NotificationRepository, provide_notifications_repo
from app.repositories.user import (
    UserRepository,
    provide_users_repo,
    provide_users_with_registrations_repo,
)


class NotificationController(Controller):
    dependencies = {
        "notifications_repo": Provide(provide_notifications_repo),
        "users_repo": Provide(provide_users_repo),
        "users_with_registrations_repo": Provide(provide_users_with_registrations_repo),
    }
    return_dto = s.NotificationDTO

    @get("/notification-key")
    async def get_notification_key(self) -> str:
        return env.VAPID_APPLICATION_SERVER_KEY

    @post("/api/v1/notifications")
    async def notify(
        self,
        notifications_repo: NotificationRepository,
        users_with_registrations_repo: UserRepository,
        webpush: WebPush,
        data: Annotated[
            s.NotificationCreate,
            Body(
                title="Send a notification",
                description="Send the notification message to a registered user",
            ),
        ],
    ) -> m.Notification:
        user: m.User | None = await users_with_registrations_repo.get_one_or_none(id=data.user_id)
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

        notification: m.Notification = await notifications_repo.add(
            m.Notification(**data.model_dump())
        )
        await notifications_repo.session.commit()
        return notification

    @get("/api/v1/users/{user_id:int}/notifications")
    async def list_notifications(
        self,
        notifications_repo: NotificationRepository,
        users_repo: UserRepository,
        user_id: int,
        unread: bool | None = None,
    ) -> list[m.Notification]:
        user: m.User | None = await users_repo.get_one_or_none(id=user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        if unread is not None:
            notifications: list[m.Notification] = await notifications_repo.list(
                order_by=(m.Notification.date, True),
                user=user,
                unread=unread,
            )
        else:
            notifications: list[m.Notification] = await notifications_repo.list(
                order_by=(m.Notification.date, True),
                user=user,
            )
        return notifications

    @patch("/api/v1/users/{user_id:int}/notification/{notification_id:int}/read")
    async def read_notification(
        self,
        notifications_repo: NotificationRepository,
        users_repo: UserRepository,
        user_id: int,
        notification_id: int,
        data: Annotated[
            s.NotificationRead,
            Body(
                description="Mark a user notification as read or unread",
            ),
        ],
    ) -> m.Notification:
        user: m.User | None = await users_repo.get_one_or_none(id=user_id)
        if user is None:
            raise NotFoundException(detail="User not found")
        notification: m.Notification | None = await notifications_repo.get_one_or_none(
            id=notification_id,
            user=user,
        )
        if notification is None:
            raise NotFoundException(detail="Notification not found")
        notification.unread = not data.read
        notification = await notifications_repo.update(notification)
        await notifications_repo.session.commit()
        return notification
