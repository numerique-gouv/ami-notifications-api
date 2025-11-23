from typing import Any

from advanced_alchemy.extensions.litestar import repository, service
from advanced_alchemy.extensions.litestar.providers import create_service_provider
from litestar import Request

from app import models


class UserService(service.SQLAlchemyAsyncRepositoryService[models.User]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.User]):
        model_type = models.User

    repository_type = Repo


provide_users_service = create_service_provider(UserService)


async def provide_user(request: Request[models.User, Any, Any]) -> models.User:
    return request.user
