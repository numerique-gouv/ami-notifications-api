from litestar import Litestar, get
from litestar.static_files import create_static_files_router

HTML_DIR = "public"


@get("/notifications/{email:str}")
async def get_notifications(email: str) -> list[str]:
    return []


app = Litestar(
    route_handlers=[
        create_static_files_router(
            path="/",
            directories=[HTML_DIR],
            html_mode=True,
        ),
        get_notifications,
    ]
)
