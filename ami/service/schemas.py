import datetime
from dataclasses import dataclass, field
from enum import Enum

from ami.utils.schemas import ExpirationRule


class ServicesSourceStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ServicesItem:
    partner_id: str
    item_type: str

    title: str
    short_description: str
    description: str
    url: str | None

    with_silent_login: bool

    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class ServicesSource:
    status: ServicesSourceStatus = field(default=ServicesSourceStatus.LOADING)
    items: list[ServicesItem] = field(default_factory=list[ServicesItem])
    expires_at: datetime.datetime | None = field(default=None)

    def set_expires_at(self, expiration_rule: ExpirationRule):
        self.expires_at = expiration_rule.compute_expires_at()


@dataclass
class Services:
    internal: ServicesSource | None = field(default_factory=ServicesSource)
