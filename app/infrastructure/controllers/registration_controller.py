# controller ou endpoint ?

@post("/notification/register")
async def register(
    db_session: AsyncSession,
    data: Annotated[
        RegistrationCreation,
        Body(
            title="Register to receive notifications",
            description="Register with a push subscription and an email to receive notifications",
        ),
    ],
) -> Registration:
    WebPushSubscription.model_validate(data.subscription)
    try:
        user = await get_user_by_email(data.email, db_session)
    except NotFoundException:
        user = User(email=data.email)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    registration = Registration(subscription=data.subscription, user_id=user.id)
    db_session.add(registration)
    await db_session.commit()
    await db_session.refresh(registration)
    return registration