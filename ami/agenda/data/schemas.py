import datetime
from dataclasses import dataclass, fields
from typing import Any

from ami.agenda.schemas import AgendaCatalogItem, AgendaCatalogItemKind


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
        start_date = datetime.datetime.fromisoformat(filtered["start_date"]).date()
        filtered["start_date"] = start_date
        # The API returns the first day back, not the last day of the school holiday
        end_date = datetime.datetime.fromisoformat(filtered["end_date"]).date()
        # Sometimes, for the Ascension Day long weekend, the API only returns the period for Thursday only,
        # not the period from Thursday through next Monday
        filtered["end_date"] = max(start_date, end_date - datetime.timedelta(days=1))
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
