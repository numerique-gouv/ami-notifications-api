from collections.abc import Iterator

import pytest
from litestar import Litestar
from litestar.testing import TestClient

from app import app

app.debug = True


@pytest.fixture(scope="function")
def test_client() -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as client:
        yield client
