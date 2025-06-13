#@dataclass
#class Registration:
#    id: int
#    user: User
#    subscription: dict[str, Any]


class SqliteDatabaseRegistration(SQLModel, table=True):
    __tablename__ = "registration"  # type: ignore

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="ami_user.id")
    user: User = Relationship(back_populates="registrations")
    subscription: dict[str, Any] = Field(sa_column=Column(JSON))