class NotificationRepository():
    @abstractmethod
    async def get(self, **filters: Any) -> Notification | None:
        pass


    @abstractmethod
    async def get_notification_list(self, user: User) -> None:
        pass