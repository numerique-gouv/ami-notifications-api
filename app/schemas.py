import datetime
import uuid
from dataclasses import dataclass, fields
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class BaseModel(PydanticBaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class FCUserInfo(BaseModel):
    birthcountry: int | None
    birthdate: datetime.date | None = None
    birthplace: int | None = None
    email: str | None = None
    family_name: str | None = None
    gender: str | None = None
    given_name: str | None = None


class Notification(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    message: str
    sender: str | None
    title: str | None
    unread: bool
    created_at: datetime.datetime


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    message: str = Field(min_length=1)
    sender: str | None
    title: str | None


class NotificationRead(BaseModel):
    read: bool


class Registration(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    subscription: dict[str, Any]
    created_at: datetime.datetime


class RegistrationCreate(BaseModel):
    user_id: uuid.UUID
    subscription: dict[str, Any]


@dataclass
class Holiday:
    description: str
    zones: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    emoji: str

    emoji_mapping = {
        "Vacances de la Toussaint": "🍁",
        "Vacances de Noël": "🎄",
        "Vacances d'Hiver": "❄️",
        "Vacances de Printemps": "🌸",
        "Vacances d'Été": "☀️",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Holiday":
        cls_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in cls_fields}
        filtered["start_date"] = datetime.datetime.fromisoformat(filtered["start_date"])
        filtered["end_date"] = datetime.datetime.fromisoformat(filtered["end_date"])
        filtered["emoji"] = cls.emoji_mapping.get(filtered["description"], "")
        return cls(**filtered)
