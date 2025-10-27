from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m


class NotificationRepository(SQLAlchemyAsyncRepository[m.Notification]):
    model_type = m.Notification


async def provide_notifications_repo(db_session: AsyncSession) -> NotificationRepository:
    return NotificationRepository(session=db_session)
