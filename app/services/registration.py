from advanced_alchemy.extensions.litestar import repository, service

from app import models as m


class RegistrationService(service.SQLAlchemyAsyncRepositoryService[m.Registration]):
    class Repo(repository.SQLAlchemyAsyncRepository[m.Registration]):
        model_type = m.Registration

    repository_type = Repo
