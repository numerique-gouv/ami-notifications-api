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
    "psl": Partner("psl", "PSL", env.PARTNERS_PSL_SECRET, ""),
    "dinum-dn": Partner(
        "dinum-dn",
        "demarche.numerique.gouv.fr",
        env.PARTNERS_DINUM_DN_SECRET,
        "fr-icon-infinity-line",
    ),
    "dinum-ami": Partner(
        "dinum-ami", "AMI", env.PARTNERS_DINUM_AMI_SECRET, "fr-icon-smartphone-line"
    ),
}


async def provide_partner(request: Request[Partner, Any, Any]) -> Partner:
    return request.user
