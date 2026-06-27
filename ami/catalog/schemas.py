import datetime
from dataclasses import dataclass, field
from enum import Enum

from ami.utils.schemas import ExpirationRule


class CatalogItemsStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class CatalogItem:
    partner_id: str
    external_item_type: str

    title: str
    short_description: str
    description: str
    external_url: str | None

    with_silent_login: bool

    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class CatalogItems:
    status: CatalogItemsStatus = field(default=CatalogItemsStatus.LOADING)
    items: list[CatalogItem] = field(default_factory=list[CatalogItem])
    expires_at: datetime.datetime | None = field(default=None)

    def set_expires_at(self, expiration_rule: ExpirationRule):
        self.expires_at = expiration_rule.compute_expires_at()


@dataclass
class Catalog:
    internal: CatalogItems | None = field(default_factory=CatalogItems)
