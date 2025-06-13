class RegistrationRepository():
    @abstractmethod
    async def get(self, **filters: Any) -> Notification | None:
        pass


    @abstractmethod
    async def create_registration(self, user: User) -> None:
        pass