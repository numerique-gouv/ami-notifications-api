#@dataclass
#class User:
#    id: int
#    email: str
#    registrations: list[Registration]
#    notifications: list[Notification]


class SqliteDatabaseUser(SQLModel, table=True):
    __tablename__ = "ami_user"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    email: str
    registrations: list["Registration"] = Relationship(back_populates="user")
    notifications: list["Notification"] = Relationship(back_populates="user")