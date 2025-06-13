# controller ou endpoint ?

@get("/notification/users")
async def list_users(db_session: AsyncSession) -> list[Registration]:
    # TODO: this should instead return a list of users, and thus use `get_user_list`.
    return await get_registration_list(db_session)