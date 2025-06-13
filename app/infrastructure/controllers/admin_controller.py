@get(path="/admin/", include_in_schema=False)
async def admin(db_session: AsyncSession) -> Template:
    users = await get_user_list(db_session)
    notifications = await get_notification_list(db_session)
    return Template(
        template_name="admin.html",
        context={"users": users, "notifications": notifications},
    )