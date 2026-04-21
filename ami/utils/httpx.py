import hashlib
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager

from django.core.cache import cache
from django.utils.encoding import smart_bytes
from httpx import URL, AsyncClient, Client, Response  # noqa


def get_cache_key(url: str):
    return hashlib.md5(smart_bytes(url)).hexdigest()


class AMIClient(Client):
    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def request(
        self,
        method: str,
        url: URL | str,
        *,
        cache_duration: int | None = None,
        **kwargs,
    ) -> Response:
        request = self.build_request(
            method,
            url,
            **{k: v for k, v in kwargs.items() if k not in ["auth", "follow_redirects"]},
        )

        cache_key = get_cache_key(str(request.url))
        if method == "GET" and cache_duration:
            cache_content = cache.get(cache_key)
            if cache_content:
                response = Response(status_code=200, content=cache_content)
                return response

        response = super().request(method, url, **kwargs)

        if method == "GET" and cache_duration and (response.status_code // 100 == 2):
            cache.set(cache_key, response.content, cache_duration)

        return response


@contextmanager
def httpxClient() -> Generator[AMIClient]:
    with AMIClient(timeout=60) as client:
        yield client


@asynccontextmanager
async def httpxAsyncClient() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(timeout=60) as client:
        yield client
