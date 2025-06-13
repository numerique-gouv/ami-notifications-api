class UserRepository():
    @abstractmethod
    async def get(self, **filters: Any) -> User | None:
        pass


    @abstractmethod
    async def create_user(self, user: User) -> None:
        pass