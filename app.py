from litestar import Litestar, get


@get("/")
async def index() -> str:
    return "Hello, world!"


@get("/notifications/{email:str}")
async def get_notifications(email: str) -> list[str]:
    return []


app = Litestar([index, get_notifications])
