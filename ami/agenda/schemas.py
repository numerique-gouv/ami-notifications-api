import datetime
from dataclasses import dataclass, field
from enum import Enum

from ami.utils.schemas import ExpirationRule


class AgendaSourceStatus(Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


class AgendaItemKind(Enum):
    MONEY = "money"
    ABROAD = "abroad"
    ENVIRONMENT = "environment"
    FAMILY = "family"
    WORK = "work"
    JUSTICE = "justice"
    PUBLIC_HOLIDAY = "public-holiday"
    HOUSING = "housing"
    LEISURE = "leisure"
    CITIZENSHIP = "citizenship"
    CARE = "care"
    TRANSPORT = "transport"
    SCHOOL_HOLIDAY = "school-holiday"
    OTHER = "other"


@dataclass
class AgendaItem:
    kinds: list[AgendaItemKind]
    title: str
    description: str = field(default="")
    date: datetime.date | None = field(default=None)
    start_date: datetime.date | None = field(default=None)
    end_date: datetime.date | None = field(default=None)
    zones: list[str] = field(default_factory=list)
    emoji: str = field(default="")
    url: str | None = field(default=None)


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
    marronniers: AgendaSource | None = field(default_factory=AgendaSource)
