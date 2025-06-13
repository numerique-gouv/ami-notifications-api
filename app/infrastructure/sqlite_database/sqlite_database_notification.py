#class SqliteDatabaseNotification:
#    id: int
#    date: datetime
#    # formattedDate aussi ?
#    user: User
#    message: str
#    sender: str
#    title: str


class SqliteDatabaseNotification(SQLModel, table=True):
    __tablename__ = "notification"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="ami_user.id")
    user: User = Relationship(back_populates="notifications")
    message: str
    sender: str | None = Field(default=None)
    title: str | None = Field(default=None)