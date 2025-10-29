from advanced_alchemy.extensions.litestar import repository, service

from app import models as m


class UserService(service.SQLAlchemyAsyncRepositoryService[m.User]):
    class Repo(repository.SQLAlchemyAsyncRepository[m.User]):
        model_type = m.User

    repository_type = Repo
