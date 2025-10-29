from advanced_alchemy.extensions.litestar import repository, service

from app import models


class RegistrationService(service.SQLAlchemyAsyncRepositoryService[models.Registration]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.Registration]):
        model_type = models.Registration

    repository_type = Repo
