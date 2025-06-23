class NotificationRepository():
    async def get(self, **filters: Any) -> Notification | None:
        pass


    async def create_notification(self, user: User) -> None:
        pass


    async def get_notification_list(db_session: AsyncSession) -> list[Notification]:
        query = select(Notification).order_by(col(Notification.date).desc())
        result = await db_session.exec(query)
        return list(result.all())