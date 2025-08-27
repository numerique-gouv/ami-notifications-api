from litestar import Router, get
from litestar.response import Template


@get(path="/", include_in_schema=False)
async def home() -> Template:
    encours = []
    return Template(
        template_name="rvo-liste.html",
        context={"encours": encours},
    )


rvo_router = Router(path="/rvo", route_handlers=[home])
