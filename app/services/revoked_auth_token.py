from advanced_alchemy.extensions.litestar import repository, service

from app import models


class RevokedAuthTokenService(service.SQLAlchemyAsyncRepositoryService[models.RevokedAuthToken]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.RevokedAuthToken]):
        model_type = models.RevokedAuthToken

    repository_type = Repo
