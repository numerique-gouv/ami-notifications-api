@dataclass
class Notification:
    def getid(): int
    def getDate(): datetime
    # formattedDate aussi ?
    def getUserRaw(): UserRaw
    def getMessage(): str
    def getSender(): str
    def getTitle(): str