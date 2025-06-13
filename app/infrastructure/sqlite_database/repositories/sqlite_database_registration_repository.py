class RegistrationRepository():
    async def get(self, **filters: Any) -> Notification | None:
        pass


    async def create_notification(self, user: User) -> None:
        pass


async def get_registration_list(
    db_session: AsyncSession,
    options: ExecutableOption | None = None,
) -> list[Registration]:
    if options:
        query = select(Registration).options(options)
    else:
        query = select(Registration)
    query = query.order_by(col(Registration.user_id))
    result = await db_session.exec(query)
    return list(result.all())