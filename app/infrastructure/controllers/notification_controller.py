# controller ou endpoint ?

SendNotificationToUser sendNotificationToUser
GetNotifications getNotifications


@post("/notification/send")
async def notify(
    db_session: AsyncSession,
    webpush: WebPush,
    data: Annotated[
        Notification,
        Body(
            title="Send a notification",
            description="Send the notification message to a registered user",
        ),
    ],
) -> Notification:
    sendNotificationToUser.execute()

///////////////
    user = await userRepository.get_user_by_id(
        data.user_id,
        db_session,
        options=selectinload(cast(InstrumentedAttribute, User.registrations)),
    )

    for registration in user.registrations:
        subscription = WebPushSubscription.model_validate(registration.subscription)
        json_data = {"title": data.title, "message": data.message, "sender": data.sender}
        message = webpush.get(message=json.dumps(json_data), subscription=subscription)
        headers = cast(dict, message.headers)

        response = httpx.post(
            registration.subscription["endpoint"], content=message.encrypted, headers=headers
        )
        response.raise_for_status()
    db_session.add(data)
    await db_session.commit()
    await db_session.refresh(data)
    return data


@get("/notifications/{email:str}")
async def get_notifications(db_session: AsyncSession, email: str) -> list[Notification]:
    try:
        user: User = await get_user_by_email(
            email, db_session, options=selectinload(cast(InstrumentedAttribute, User.notifications))
        )
    except NotFoundException:
        return []
    return user.notifications