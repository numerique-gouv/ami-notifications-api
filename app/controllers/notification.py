from typing import Annotated

from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Response, get, post
from litestar.background_tasks import BackgroundTask
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.exceptions import (
    NotFoundException,
)
from litestar.params import Body
from webpush import WebPush

from app import env, models, schemas, sentry
from app.httpx import AsyncClient
from app.partners import Partner, provide_partner
from app.services.notification import NotificationService
from app.services.user import UserService


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
    async def admin_create_notification(
        self,
        channels: ChannelsPlugin,
        notifications_service: NotificationService,
        users_with_registrations_service: UserService,
        webpush: WebPush,
        data: schemas.AdminNotificationCreate,
        httpx_async_client: AsyncClient,
    ) -> Response[schemas.NotificationResponse]:
        user: models.User | None = await users_with_registrations_service.get_one_or_none(
            id=data.user_id
        )
        if user is None:
            raise NotFoundException(detail="User not found")

        notification: models.Notification = await notifications_service.create(
            models.Notification(**data.model_dump())
        )

        # Push notification in background after DB transaction completes
        background_task = BackgroundTask(
            NotificationService.push_notification,
            channels,
            webpush,
            notification.id,
            True,
            httpx_async_client,
        )

        response_data = schemas.NotificationResponse.model_validate(
            {
                "notification_id": notification.id,
                "notification_send_status": True,
            }
        )
        return Response(content=response_data, background=background_task)


class PartnerNotificationController(Controller):
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
        httpx_async_client: AsyncClient,
    ) -> Response[schemas.NotificationResponse]:
        ignore_unknown_user = env.IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER
        user: models.User | None = await users_with_registrations_service.get_one_or_none(
            fc_hash=data.recipient_fc_hash
        )
        if user is None:
            if ignore_unknown_user:
                raise NotFoundException(detail="User not found")
            user = await users_with_registrations_service.create(
                models.User(fc_hash=data.recipient_fc_hash)
            )
            notification_send_status = False
        else:
            if ignore_unknown_user and user.last_logged_in is None:
                raise NotFoundException(detail="User never seen")
            notification_send_status = user.last_logged_in is not None

        try_push = True
        if not data.try_push or user.last_logged_in is None:
            # don't push notification if not required or if user has never logged in on AMI
            try_push = False

        notification_data = data.model_dump()
        notification_data.pop("recipient_fc_hash")
        if notification_data["content_icon"] is None:
            notification_data["content_icon"] = current_partner.icon or "fr-icon-mail-star-line"
        notification_data["sender"] = current_partner.name
        notification_data["partner_id"] = current_partner.id
        notification_data["send_status"] = notification_send_status
        notification: models.Notification = await notifications_service.create(
            models.Notification(user_id=user.id, **notification_data)
        )
        background_task = BackgroundTask(
            NotificationService.push_notification,
            channels,
            webpush,
            notification.id,
            try_push,
            httpx_async_client,
        )

        sentry.add_counter("notification_partner.created")

        response_data = schemas.NotificationResponse.model_validate(
            {
                "notification_id": notification.id,
                "notification_send_status": notification_send_status,
            }
        )
        return Response(content=response_data, background=background_task)
