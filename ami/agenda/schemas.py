import datetime
from dataclasses import dataclass, field
from enum import Enum

from ami.utils.schemas import ExpirationRule


class AgendaSourceStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


class AgendaItemKind(Enum):
    HOLIDAY = "holiday"
    ELECTION = "election"


@dataclass
class AgendaItem:
    kind: AgendaItemKind
    title: str
    description: str = field(default="")
    date: datetime.date | None = field(default=None)
    start_date: datetime.date | None = field(default=None)
    end_date: datetime.date | None = field(default=None)
    zones: list[str] = field(default_factory=list)
    emoji: str = field(default="")


@dataclass
class AgendaSource:
    status: AgendaSourceStatus = field(default=AgendaSourceStatus.LOADING)
    items: list[AgendaItem] = field(default_factory=list[AgendaItem])
    expires_at: datetime.datetime | None = field(default=None)

    def set_expires_at(self, expiration_rule: ExpirationRule):
        self.expires_at = expiration_rule.compute_expires_at()


@dataclass
class Agenda:
    school_holidays: AgendaSource | None = field(default_factory=AgendaSource)
    public_holidays: AgendaSource | None = field(default_factory=AgendaSource)
    elections: AgendaSource | None = field(default_factory=AgendaSource)
