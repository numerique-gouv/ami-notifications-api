from advanced_alchemy.extensions.litestar import repository, service

from app import models


class NonceService(service.SQLAlchemyAsyncRepositoryService[models.Nonce]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.Nonce]):
        model_type = models.Nonce

    repository_type = Repo
