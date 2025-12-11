from typing import Annotated

from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Response, post
from litestar.di import Provide
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
)

from app import models, schemas
from app.services.scheduled_notification import ScheduledNotificationService
from app.services.user import provide_user


class ScheduledNotificationController(Controller):
    dependencies = {
        "current_user": Provide(provide_user),
        "scheduled_notifications_service": providers.create_service_provider(
            ScheduledNotificationService
        ),
    }

    @post("/api/v1/users/scheduled-notifications")
    async def create_scheduled_notification(
        self,
        scheduled_notifications_service: ScheduledNotificationService,
        data: Annotated[
            schemas.ScheduledNotificationCreate,
            Body(
                title="Send a scheduled notification",
                description="Send the scheduled notification message to a registered user",
            ),
        ],
        current_user: models.User,
    ) -> Response[schemas.ScheduledNotificationResponse]:
        existing_scheduled_notification: (
            models.ScheduledNotification | None
        ) = await scheduled_notifications_service.get_one_or_none(
            reference=data.reference, user=current_user
        )
        status_code = HTTP_200_OK
        if existing_scheduled_notification is None:
            # create scheduled notification
            scheduled_notification: models.ScheduledNotification = (
                await scheduled_notifications_service.create(
                    models.ScheduledNotification(
                        user_id=current_user.id, sender="AMI", **data.model_dump()
                    )
                )
            )
            status_code = HTTP_201_CREATED
        elif existing_scheduled_notification.sent_at is None:
            # update scheduled notification
            scheduled_notification: models.ScheduledNotification = (
                await scheduled_notifications_service.update(
                    data, item_id=existing_scheduled_notification.id
                )
            )
        else:
            # scheduled notification was already sent as a notification to user:
            # don't change it
            scheduled_notification: models.ScheduledNotification = existing_scheduled_notification

        response_data = schemas.ScheduledNotificationResponse.model_validate(
            {
                "scheduled_notification_id": scheduled_notification.id,
            }
        )
        return Response(content=response_data, status_code=status_code)
