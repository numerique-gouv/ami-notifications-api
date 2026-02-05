import os
from typing import Any

from litestar import Request
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler
from litestar.response.redirect import Redirect

AMI_ADMIN_RESTRICTED_ACCESS = os.getenv("AMI_ADMIN_RESTRICTED_ACCESS", "true")
AMI_ADMIN_RESTRICTED_TO = os.getenv("AMI_ADMIN_RESTRICTED_TO", "")


def is_not_connected(session: dict[str, Any]) -> bool:
    return "userinfo" not in session or "id_token" not in session


def access_authorized(session: dict[str, Any]) -> bool:
    user_email = session["userinfo"]["email"]
    if AMI_ADMIN_RESTRICTED_ACCESS.lower() == "false":
        return True
    authorized_emails = AMI_ADMIN_RESTRICTED_TO.split(",")
    authorized_emails = [e.strip() for e in authorized_emails if e.strip()]
    if user_email in authorized_emails:
        return True
    return False


def authenticated_guard(
    connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler
) -> None:
    if is_not_connected(connection.session):
        connection.session["redirect_once_connected"] = str(connection.url)
        raise NotAuthenticatedException

    if not access_authorized(connection.session):
        raise AccessNotAuthorizedException

    if "redirect_once_connected" in connection.session:
        del connection.session["redirect_once_connected"]  # Not useful anymore.


class NotAuthenticatedException(NotAuthorizedException):
    pass


class AccessNotAuthorizedException(NotAuthorizedException):
    pass


def redirect_to_login_exception_handler(request: Request[Any, Any, Any], _: Exception) -> Redirect:
    return Redirect("/ami_admin")


def redirect_to_unauthorized_exception_handler(
    request: Request[Any, Any, Any], _: Exception
) -> Redirect:
    return Redirect("/ami_admin/unauthorized")
