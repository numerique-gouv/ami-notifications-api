from typing import Any

from litestar import Litestar
from litestar.testing import TestClient as LTTestClient

from app.models import User


class TestClient(LTTestClient[Litestar]):
    user: User | None = None
    userinfo: dict[str, Any] | None = None


class ConnectedTestClient(LTTestClient[Litestar]):
    user: User
    userinfo: dict[str, Any]
