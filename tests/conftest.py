import sys
from collections.abc import Iterator

import pytest
from litestar import Litestar
from litestar.testing import TestClient

# FIXME: this is a hack, should be resolved by a better code/package structure.
sys.path.append(".")

from app import app

app.debug = True


@pytest.fixture(scope="function")
def test_client() -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as client:
        yield client
