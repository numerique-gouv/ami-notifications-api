from advanced_alchemy.extensions.litestar import repository, service

from app import models as m


class NotificationService(service.SQLAlchemyAsyncRepositoryService[m.Notification]):
    class Repo(repository.SQLAlchemyAsyncRepository[m.Notification]):
        model_type = m.Notification

    repository_type = Repo
