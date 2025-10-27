from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m


class UserRepository(SQLAlchemyAsyncRepository[m.User]):
    model_type = m.User


async def provide_users_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)


async def provide_users_with_registrations_repo(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session, load=[m.User.registrations])
