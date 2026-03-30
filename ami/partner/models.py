from dataclasses import dataclass

from django.conf import settings


@dataclass
class Partner:
    id: str
    name: str
    secret: str
    icon: str
    followup_from_notifications: bool = True


partners: dict[str, Partner] = {
    "psl": Partner(
        "psl",
        "PSL",
        settings.PARTNERS_PSL_SECRET,
        "",
    ),
    "dinum-dn": Partner(
        "dinum-dn",
        "demarche.numerique.gouv.fr",
        settings.PARTNERS_DINUM_DN_SECRET,
        "fr-icon-infinity-line",
    ),
    "dinum-ami": Partner(
        "dinum-ami",
        "AMI",
        settings.PARTNERS_DINUM_AMI_SECRET,
        "fr-icon-smartphone-line",
    ),
}
