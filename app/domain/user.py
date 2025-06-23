@dataclass
class User:
    id: int
    email: str
    registrations: list[Registration]
    notifications: list[Notification]

    User(UserRaw userRaw)
        id = userRaw.getId()
        email = userRaw.getEmail()
        registrations = userRaw.getRegistrationRaws.stream()
            .map(registrationRaw -> Registration.factory.create(registrationRaw))
            .collect(toList())
        notifications = userRaw.getNotificationRaws.stream()
            .map(notificationnRaw -> Notification.factory.create(notificationRaw))
            .collect(toList())
    
    class Factory
        User create(UserRaw userRaw)
            return new User(userRaw)