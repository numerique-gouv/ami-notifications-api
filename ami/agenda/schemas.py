import datetime
from dataclasses import dataclass, field
from enum import Enum

from ami.utils.schemas import ExpirationRule


class AgendaCatalogStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


class AgendaCatalogItemKind(Enum):
    HOLIDAY = "holiday"
    ELECTION = "election"


@dataclass
class AgendaCatalogItem:
    kind: AgendaCatalogItemKind
    title: str
    description: str = field(default="")
    date: datetime.date | None = field(default=None)
    start_date: datetime.date | None = field(default=None)
    end_date: datetime.date | None = field(default=None)
    zones: list[str] = field(default_factory=list)
    emoji: str = field(default="")


@dataclass
class AgendaCatalog:
    status: AgendaCatalogStatus = field(default=AgendaCatalogStatus.LOADING)
    items: list[AgendaCatalogItem] = field(default_factory=list[AgendaCatalogItem])
    expires_at: datetime.datetime | None = field(default=None)

    def set_expires_at(self, expiration_rule: ExpirationRule):
        self.expires_at = expiration_rule.compute_expires_at()


@dataclass
class Agenda:
    school_holidays: AgendaCatalog | None = field(default_factory=AgendaCatalog)
    public_holidays: AgendaCatalog | None = field(default_factory=AgendaCatalog)
    elections: AgendaCatalog | None = field(default_factory=AgendaCatalog)
