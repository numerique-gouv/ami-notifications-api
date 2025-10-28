from advanced_alchemy.extensions.litestar import repository, service
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m


class UserService(service.SQLAlchemyAsyncRepositoryService[m.User]):
    class Repo(repository.SQLAlchemyAsyncRepository[m.User]):
        model_type = m.User

    repository_type = Repo


async def provide_users_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session)


async def provide_users_with_registrations_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session, load=[m.User.registrations])
