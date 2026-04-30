from django.core.cache import cache
from pytest_httpx import HTTPXMock

from ami.utils.httpx import URL, get_cache_key, httpxClient


def test_httpx_request_without_cache(
    app,
    httpx_mock: HTTPXMock,
):
    with httpxClient() as httpx_client:
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get("http://foo/bar")
        assert response.json() == {"foo": "bar"}

        # again, no cache here
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get("http://foo/bar")
        assert response.json() == {"foo": "bar"}


def test_httpx_request_with_cache(
    app,
    httpx_mock: HTTPXMock,
):
    with httpxClient() as httpx_client:
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get("http://foo/bar", cache_duration=1)
        assert response.json() == {"foo": "bar"}

        # again, value in cache
        response = httpx_client.get("http://foo/bar", cache_duration=1)
        assert response.json() == {"foo": "bar"}

        # new url
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get("http://foo/baz", cache_duration=1)
        assert response.json() == {"foo": "bar"}


def test_httpx_request_with_cache_with_params(
    app,
    httpx_mock: HTTPXMock,
):
    with httpxClient() as httpx_client:
        httpx_mock.add_response(json={"foo": "bar1"})
        response = httpx_client.get("http://foo/bar", params={"key": "value1"}, cache_duration=1)
        assert response.json() == {"foo": "bar1"}

        # other params
        httpx_mock.add_response(json={"foo": "bar2"})
        response = httpx_client.get("http://foo/bar", params={"key": "value2"}, cache_duration=1)
        assert response.json() == {"foo": "bar2"}

        # again, value in cache
        response = httpx_client.get("http://foo/bar", params={"key": "value2"}, cache_duration=1)
        assert response.json() == {"foo": "bar2"}


def test_httpx_request_with_cache_expired(
    app,
    httpx_mock: HTTPXMock,
):
    # cache is expired
    cache_key = get_cache_key("http://foo/bar")
    cache.set(cache_key, "content", 0)

    with httpxClient() as httpx_client:
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get("http://foo/bar", cache_duration=1)
        assert response.json() == {"foo": "bar"}


def test_httpx_request_dont_use_cache(
    app,
    httpx_mock: HTTPXMock,
):
    with httpxClient() as httpx_client:
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get("http://foo/bar", cache_duration=1)
        assert response.json() == {"foo": "bar"}

        # no cache_duration, don't get value in cache
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get("http://foo/bar")
        assert response.json() == {"foo": "bar"}


def test_httpx_request_with_URL(
    app,
    httpx_mock: HTTPXMock,
):
    with httpxClient() as httpx_client:
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get(URL("http://foo/bar"), cache_duration=1)
        assert response.json() == {"foo": "bar"}

        response = httpx_client.get(URL("http://foo/bar"), cache_duration=1)
        assert response.json() == {"foo": "bar"}


def test_httpx_request_with_URL_and_params(
    app,
    httpx_mock: HTTPXMock,
):
    with httpxClient() as httpx_client:
        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get(URL("http://foo/bar"), cache_duration=1)
        assert response.json() == {"foo": "bar"}

        httpx_mock.add_response(json={"foo": "bar"})
        response = httpx_client.get(
            URL("http://foo/bar"), params={"key": "value"}, cache_duration=1
        )
        assert response.json() == {"foo": "bar"}

        response = httpx_client.get(
            URL("http://foo/bar"), params={"key": "value"}, cache_duration=1
        )
        assert response.json() == {"foo": "bar"}

        response = httpx_client.get(URL("http://foo/bar?key=value"), cache_duration=1)
        assert response.json() == {"foo": "bar"}
