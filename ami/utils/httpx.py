from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from httpx import AsyncClient, Client

httpxClient = Client(timeout=60)


@asynccontextmanager
async def httpxAsyncClient() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(timeout=60) as client:
        yield client
