from advanced_alchemy.extensions.litestar import repository, service

from app import models


class NotificationService(service.SQLAlchemyAsyncRepositoryService[models.Notification]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.Notification]):
        model_type = models.Notification

    repository_type = Repo
