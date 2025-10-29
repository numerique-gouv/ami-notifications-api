from advanced_alchemy.extensions.litestar import repository, service

from app import models


class UserService(service.SQLAlchemyAsyncRepositoryService[models.User]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.User]):
        model_type = models.User

    repository_type = Repo
