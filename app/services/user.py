from typing import Any

from advanced_alchemy.extensions.litestar import repository, service
from litestar import Request

from app import models


class UserService(service.SQLAlchemyAsyncRepositoryService[models.User]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.User]):
        model_type = models.User

    repository_type = Repo


async def provide_user(request: Request[models.User, Any, Any]) -> models.User:
    return request.user
