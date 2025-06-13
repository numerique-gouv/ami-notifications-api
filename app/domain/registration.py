@dataclass
class Registration:
    id: int
    user: User
    subscription: dict[str, Any]