import os

from litestar import Router, get
from litestar.response import Template

PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID = os.getenv("PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID", "")
PUBLIC_FC_BASE_URL = os.getenv("PUBLIC_FC_BASE_URL", "")
PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL = os.getenv("PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL", "")
PUBLIC_FC_AUTHORIZATION_ENDPOINT = os.getenv("PUBLIC_FC_AUTHORIZATION_ENDPOINT", "")


@get(path="/", include_in_schema=False)
async def home() -> Template:
    encours = []
    return Template(
        template_name="rvo-liste.html",
        context={
            "encours": encours,
            "isFranceConnected": True,
            "PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID": PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID,
            "PUBLIC_FC_BASE_URL": PUBLIC_FC_BASE_URL,
            "PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL": PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL,
            "PUBLIC_FC_AUTHORIZATION_ENDPOINT": PUBLIC_FC_AUTHORIZATION_ENDPOINT,
        },
    )


rvo_router = Router(path="/rvo", route_handlers=[home])
