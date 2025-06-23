async def execute(
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
    userRaw = await userRawRepository.get_user_by_id(user_id)

    Notification.factory.create(userRaw)
    