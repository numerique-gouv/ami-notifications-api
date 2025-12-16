import datetime
import uuid

from advanced_alchemy.extensions.litestar import repository, service
from advanced_alchemy.extensions.litestar.providers import create_service_provider
from litestar import Litestar
from litestar.channels import ChannelsPlugin
from sqlalchemy import select

from app import models
from app.services.notification import NotificationService
from app.webpush import provide_webpush


class ScheduledNotificationService(
    service.SQLAlchemyAsyncRepositoryService[models.ScheduledNotification]
):
    class Repo(repository.SQLAlchemyAsyncRepository[models.ScheduledNotification]):
        model_type = models.ScheduledNotification

    repository_type = Repo

    async def publish_scheduled_notifications(self, app: Litestar):
        now = datetime.datetime.now(datetime.timezone.utc)
        scheduled_notifications = await self.list(
            models.ScheduledNotification.scheduled_at < now,
            models.ScheduledNotification.sent_at.is_(None),
            order_by=(models.ScheduledNotification.created_at, False),
        )
        for scheduled_notification in scheduled_notifications:
            await self.publish_scheduled_notification(scheduled_notification.id, app)

    async def publish_scheduled_notification(
        self, scheduled_notification_id: uuid.UUID, app: Litestar
    ):
        provide_notifications_service = create_service_provider(NotificationService)
        notifications_service: NotificationService = await anext(
            provide_notifications_service(self.repository.session)
        )
        channels: ChannelsPlugin = app.plugins.get(ChannelsPlugin)
        webpush = provide_webpush()

        now = datetime.datetime.now(datetime.timezone.utc)
        query = (
            select(models.ScheduledNotification)
            .where(
                models.ScheduledNotification.id == scheduled_notification_id,
                models.ScheduledNotification.scheduled_at < now,
                models.ScheduledNotification.sent_at.is_(None),
            )
            .with_for_update()
        )

        result = await self.repository.session.execute(query)
        scheduled_notification = result.scalar_one_or_none()
        if not scheduled_notification:
            return

        notification = await notifications_service.create(
            data={
                "user_id": scheduled_notification.user_id,
                "content_title": scheduled_notification.content_title,
                "content_body": scheduled_notification.content_body,
                "content_icon": scheduled_notification.content_icon,
                "sender": scheduled_notification.sender,
            }
        )

        await self.update(
            item_id=scheduled_notification.id,
            data={"sent_at": notification.created_at},
        )
        await self.repository.session.commit()
        await NotificationService.push_notification(
            channels,
            webpush,
            notification.id,
            True,
        )

    async def delete_published_scheduled_notifications(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        await self.delete_where(
            models.ScheduledNotification.sent_at < now - datetime.timedelta(days=6 * 30),
        )
