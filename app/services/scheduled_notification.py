from advanced_alchemy.extensions.litestar import repository, service

from app import models


class ScheduledNotificationService(
    service.SQLAlchemyAsyncRepositoryService[models.ScheduledNotification]
):
    class Repo(repository.SQLAlchemyAsyncRepository[models.ScheduledNotification]):
        model_type = models.ScheduledNotification

    repository_type = Repo
