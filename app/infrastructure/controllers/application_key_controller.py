@get("/notification/key")
async def get_application_key() -> str:
    return os.getenv("VAPID_APPLICATION_SERVER_KEY", "")