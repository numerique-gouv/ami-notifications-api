from dataclasses import dataclass
from typing import Any

from litestar import Request

from app import env


@dataclass
class Partner:
    id: str
    name: str
    secret: str
    icon: str


partners: dict[str, Partner] = {
    "psl": Partner("psl", "PSL", env.PARTNERS_PSL_SECRET, "fr-icon-megaphone-line")
}


async def provide_partner(request: Request[Partner, Any, Any]) -> Partner:
    return request.user
