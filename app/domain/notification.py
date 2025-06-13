@dataclass
class Notification:
    id: int
    date: datetime
    # formattedDate aussi ?
    user: User
    message: str
    sender: str
    title: str