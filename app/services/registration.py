from advanced_alchemy.extensions.litestar import repository, service
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


class RegistrationService(service.SQLAlchemyAsyncRepositoryService[models.Registration]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.Registration]):
        model_type = models.Registration

    repository_type = Repo


async def provide_registrations_service(db_session: AsyncSession) -> RegistrationService:
    return RegistrationService(session=db_session)
