class SqliteDatabaseUserRepository(UserRepository):
    async def get(self, **filters: Any) -> User | None:
        pass

    
    async def create_user(self, user: User) -> None:
        pass


async def get_user_by_id(
    user_id: int, db_session: AsyncSession, options: ExecutableOption | None = None
) -> User:
    if options:
        query = select(User).where(col(User.id) == user_id).options(options)
    else:
        query = select(User).where(col(User.id) == user_id)
    result = await db_session.exec(query)
    try:
        return result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User with id {user_id!r} not found") from e


async def get_user_by_email(
    email: str, db_session: AsyncSession, options: ExecutableOption | None = None
) -> User:
    if options:
        query = select(User).where(col(User.email) == email).options(options)
    else:
        query = select(User).where(col(User.email) == email)
    result = await db_session.exec(query)
    try:
        return result.one()
    except NoResultFound as e:
        raise NotFoundException(detail=f"User {email!r} not found") from e
    

async def get_user_list(
    db_session: AsyncSession,
    options: ExecutableOption | None = None,
) -> list[User]:
    if options:
        query = select(User).options(options)
    else:
        query = select(User)
    query = query.order_by(col(User.id))
    result = await db_session.exec(query)
    return list(result.all())