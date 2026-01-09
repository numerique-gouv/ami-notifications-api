from typing import Any

from litestar import Request
from litestar.response.redirect import Redirect

from app import env


class TechnicalError(Exception):
    pass


def technical_error_handler(_: Request[Any, Any, Any], exc: Exception) -> Redirect:
    return Redirect(f"{env.PUBLIC_APP_URL}/#/technical-error")
