"""Setup any system wide httpx configuration here."""

from httpx import AsyncClient
from litestar import Litestar
from litestar.datastructures import State


def get_httpx_async_client(app: Litestar):
    if not getattr(app.state, "httpx_async_client", None):
        app.state.httpx_async_client = AsyncClient(timeout=60)


async def close_httpx_async_client(app: Litestar):
    if getattr(app.state, "httpx_async_client", None):
        await app.state.httpx_async_client.aclose()


async def httpx_async_client_provider(state: State) -> AsyncClient:
    return state.httpx_async_client
