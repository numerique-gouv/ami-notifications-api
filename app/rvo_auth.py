from typing import Any

from litestar import Request
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler
from litestar.response.redirect import Redirect


def is_not_connected(session: dict[str, Any]) -> bool:
    return "userinfo" not in session or "id_token" not in session


def authenticated_guard(
    connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler
) -> None:
    if is_not_connected(connection.session):
        connection.session["redirect_once_connected"] = str(connection.url)
        raise NotAuthenticatedException

    if "redirect_once_connected" in connection.session:
        del connection.session["redirect_once_connected"]  # Not useful anymore.


class NotAuthenticatedException(NotAuthorizedException):
    pass


def redirect_to_login_exception_handler(request: Request[Any, Any, Any], _: Exception) -> Redirect:
    return Redirect("/rvo")
