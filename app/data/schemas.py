import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any


class TimeUnit(str, Enum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


@dataclass
class ExpirationRule(ABC):
    @abstractmethod
    def compute_expires_at(self) -> datetime.datetime:
        pass


@dataclass
class DurationExpiration(ExpirationRule):
    amount: int
    unit: TimeUnit

    def __init__(self, amount: int, unit: TimeUnit):
        super().__init__()
        self.amount = amount
        self.unit = unit

    def compute_expires_at(self) -> datetime.datetime:
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = datetime.timedelta(**{self.unit.value: self.amount})
        return now + delta


@dataclass
class MonthlyExpiration(ExpirationRule):
    def compute_expires_at(self) -> datetime.datetime:
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            return datetime.datetime(
                year=now.year, month=now.month + 1, day=1, tzinfo=datetime.timezone.utc
            )
        except ValueError:
            return datetime.datetime(
                year=now.year + 1, month=1, day=1, tzinfo=datetime.timezone.utc
            )


@dataclass
class SchoolHoliday:
    description: str
    zones: str
    start_date: datetime.date
    end_date: datetime.date
    emoji: str

    emoji_mapping = {
        "Vacances de la Toussaint": "🍁",
        "Vacances de Noël": "🎄",
        "Vacances d'Hiver": "❄️",
        "Vacances de Printemps": "🌸",
        "Vacances d'Été": "☀️",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SchoolHoliday":
        cls_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in cls_fields}
        filtered["start_date"] = datetime.datetime.fromisoformat(filtered["start_date"]).date()
        filtered["end_date"] = datetime.datetime.fromisoformat(filtered["end_date"]).date()
        filtered["emoji"] = cls.emoji_mapping.get(filtered["description"], "")
        return cls(**filtered)

    def to_catalog_item(self):
        return AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title=self.description,
            zones=self.zones,
            start_date=self.start_date,
            end_date=self.end_date,
            emoji=self.emoji,
        )


@dataclass
class PublicHoliday:
    description: str
    date: datetime.date
    emoji: str

    description_mapping = {
        "All Saints Day": "Toussaint",
        "Armistice Day": "Armistice 1918",
        "Ascension Thursday": "Ascension",
        "Assumption of Mary to Heaven": "Assomption",
        "Bastille Day": "Fête Nationale",
        "Christmas Day": "Noël",
        "Easter Monday": "Lundi de Pâques",
        "Labour Day": "Fête du Travail",
        "New year": "Jour de l’An",
        "Victory in Europe Day": "Victoire 1945",
        "Whit Monday": "Lundi de Pentecôte",
    }

    default_emoji = "📅"
    emoji_mapping = {
        "Bastille Day": "🎆",
        "New year": "🎉",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PublicHoliday":
        cls_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in cls_fields}
        original_description = filtered["description"]
        filtered["description"] = cls.description_mapping.get(
            original_description, original_description
        )
        filtered["emoji"] = cls.emoji_mapping.get(original_description, cls.default_emoji)
        return cls(**filtered)

    def to_catalog_item(self):
        return AgendaCatalogItem(
            kind=AgendaCatalogItemKind.HOLIDAY,
            title=self.description,
            date=self.date,
            emoji=self.emoji,
        )


@dataclass
class Election:
    title: str
    description: str
    date: datetime.date
    emoji: str

    default_emoji = "🗳️"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Election":
        cls_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in cls_fields}
        filtered["emoji"] = cls.default_emoji
        return cls(**filtered)

    def to_catalog_item(self):
        return AgendaCatalogItem(
            kind=AgendaCatalogItemKind.ELECTION,
            title=self.title,
            description=self.description,
            date=self.date,
            emoji=self.emoji,
        )


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
    zones: str = field(default="")
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
