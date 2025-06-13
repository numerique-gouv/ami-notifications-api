@dataclass
class User:
    id: int
    email: str
    registrations: list[Registration]
    notifications: list[Notification]