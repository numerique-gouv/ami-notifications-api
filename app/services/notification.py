from advanced_alchemy.extensions.litestar import repository, service
from sqlalchemy.ext.asyncio import AsyncSession

from app import models


class NotificationService(service.SQLAlchemyAsyncRepositoryService[models.Notification]):
    class Repo(repository.SQLAlchemyAsyncRepository[models.Notification]):
        model_type = models.Notification

    repository_type = Repo


async def provide_notifications_service(db_session: AsyncSession) -> NotificationService:
    return NotificationService(session=db_session)
