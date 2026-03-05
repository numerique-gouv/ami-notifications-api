import datetime

from advanced_alchemy.extensions.litestar import repository, service

from app import models


class ScheduledNotificationService(
    service.SQLAlchemyAsyncRepositoryService[models.ScheduledNotification]
):
    class Repo(repository.SQLAlchemyAsyncRepository[models.ScheduledNotification]):
        model_type = models.ScheduledNotification

    repository_type = Repo

    async def create_welcome_scheduled_notification(
        self, user: models.User
    ) -> models.ScheduledNotification | None:
        existing_scheduled_notification: (
            models.ScheduledNotification | None
        ) = await self.get_one_or_none(reference="ami:welcome", user=user)
        if existing_scheduled_notification:
            # ignore: this should not happen
            return
        scheduled_notification = await self.create(
            data={
                "user_id": user.id,
                "content_title": "Bienvenue sur AMI 👋",
                "content_body": "Ici, vous pourrez gérer votre vie administrative, suivre l'avancement de vos démarches et recevoir des rappels personnalisés.",
                "content_icon": "fr-icon-information-line",
                "reference": "ami:welcome",
                "scheduled_at": datetime.datetime.now(datetime.timezone.utc),
                "sender": "AMI",
            }
        )
        return scheduled_notification
