from dataclasses import dataclass

from django.conf import settings


@dataclass
class OldPartner:
    id: str
    name: str
    secret: str
    icon: str
    consent_is_enabled: bool
    followup_from_notifications: bool = True


partners: dict[str, OldPartner] = {
    "psl": OldPartner(
        "psl",
        "PSL",
        settings.PARTNERS_PSL_SECRET,
        "",
        settings.CONSENT_PSL_ENABLED,
    ),
    "dinum-dn": OldPartner(
        "dinum-dn",
        "demarche.numerique.gouv.fr",
        settings.PARTNERS_DINUM_DN_SECRET,
        "fr-icon-infinity-line",
        settings.CONSENT_DINUM_DN_ENABLED,
    ),
    "dinum-ami": OldPartner(
        "dinum-ami",
        "AMI",
        settings.PARTNERS_DINUM_AMI_SECRET,
        "fr-icon-smartphone-line",
        settings.CONSENT_DINUM_AMI_ENABLED,
    ),
    "dinum-rdvsp": OldPartner(
        "dinum-rdvsp",
        "RDV SP",
        settings.PARTNERS_DINUM_RDVSP_SECRET,
        "",
        settings.CONSENT_DINUM_RDVSP_ENABLED,
    ),
}
