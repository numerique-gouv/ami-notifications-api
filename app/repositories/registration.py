from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m


class RegistrationRepository(SQLAlchemyAsyncRepository[m.Registration]):
    model_type = m.Registration


async def provide_registrations_repo(db_session: AsyncSession) -> RegistrationRepository:
    return RegistrationRepository(session=db_session)
