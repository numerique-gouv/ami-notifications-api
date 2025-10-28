from advanced_alchemy.extensions.litestar import repository, service
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m


class RegistrationService(service.SQLAlchemyAsyncRepositoryService[m.Registration]):
    class Repo(repository.SQLAlchemyAsyncRepository[m.Registration]):
        model_type = m.Registration

    repository_type = Repo


async def provide_registrations_service(db_session: AsyncSession) -> RegistrationService:
    return RegistrationService(session=db_session)
