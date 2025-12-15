from typing import Any

from litestar import Litestar
from litestar.testing import TestClient as LTTestClient

from app.models import User


class TestClient(LTTestClient[Litestar]):
    app: Litestar  # to be able to use test_client.app without typing errors

    user: User | None = None
    userinfo: dict[str, Any] | None = None


class ConnectedTestClient(LTTestClient[Litestar]):
    app: Litestar  # to be able to use test_client.app without typing errors

    user: User
    userinfo: dict[str, Any]
