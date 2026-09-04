import datetime
from dataclasses import dataclass, field
from enum import Enum

from ami.utils.schemas import ExpirationRule


class PartnersSourceStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"


@dataclass
class PartnersItem:
    slug: str
    name: str
    link: str
    consent_is_enabled: bool


@dataclass
class PartnersSource:
    status: PartnersSourceStatus = field(default=PartnersSourceStatus.LOADING)
    items: list[PartnersItem] = field(default_factory=list[PartnersItem])
    expires_at: datetime.datetime | None = field(default=None)

    def set_expires_at(self, expiration_rule: ExpirationRule):
        self.expires_at = expiration_rule.compute_expires_at()
