from dataclasses import dataclass

from django.conf import settings


@dataclass
class Partner:
    id: str
    name: str
    secret: str
    icon: str


partners: dict[str, Partner] = {
    "psl": Partner("psl", "PSL", settings.CONFIG["PARTNERS_PSL_SECRET"], ""),
    "dinum-dn": Partner(
        "dinum-dn",
        "demarche.numerique.gouv.fr",
        settings.CONFIG["PARTNERS_DINUM_DN_SECRET"],
        "fr-icon-infinity-line",
    ),
    "dinum-ami": Partner(
        "dinum-ami", "AMI", settings.CONFIG["PARTNERS_DINUM_AMI_SECRET"], "fr-icon-smartphone-line"
    ),
}
