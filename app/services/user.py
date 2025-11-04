from advanced_alchemy.extensions.litestar import repository, service
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


class UserService(service.SQLAlchemyAsyncRepositoryService[models.User]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.User]):
        model_type = models.User

    repository_type = Repo


async def provide_users_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)


async def provide_users_with_registrations_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session, load=[models.User.registrations])
