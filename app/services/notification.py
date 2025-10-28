from advanced_alchemy.extensions.litestar import repository, service
from sqlalchemy.ext.asyncio import AsyncSession

from app import models as m


class NotificationService(service.SQLAlchemyAsyncRepositoryService[m.Notification]):
    class Repo(repository.SQLAlchemyAsyncRepository[m.Notification]):
        model_type = m.Notification

    repository_type = Repo


async def provide_notifications_service(db_session: AsyncSession) -> NotificationService:
    return NotificationService(session=db_session)
