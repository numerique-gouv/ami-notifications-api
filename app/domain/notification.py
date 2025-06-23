@dataclass
class Notification:
    id: int
    date: datetime
    # formattedDate aussi ?
    user: User
    message: str
    sender: str
    title: str

    Notification(NotificationRaw notificationRaw)
        id = notificationRaw.getId()
        date = notificationRaw.getDatetime()
        # formattedDate aussi ?
        user = User.factory.create(notificationRaw.getUserRaw())
        message = notificationRaw.getMessage()
        sender = notificationRaw.getSender()
        title = notificationRaw.getTitle()
    
    class Factory
        Notification create(NotificationRaw notificationRaw)
            return new Notification(notificationRaw)