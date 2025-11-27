import datetime
import uuid
from dataclasses import dataclass, fields
from enum import Enum
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


class AdminNotification(BaseModel):
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


class NotificationEvent(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class Registration(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    subscription: dict[str, Any]
    created_at: datetime.datetime


class RegistrationCreate(BaseModel):
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


class ItemGenericStatus(Enum):
    NEW = "new"
    WIP = "wip"
    CLOSED = "closed"


class NotificationPivotHashCreate(BaseModel):
    recipient_fc_hash: str
    # Dans AMI, on stocke la liste des partenaires et leur clé d'API (en base ou en variables d'env)
    # Dans la table Notifications, il y a le partenaire émetteur
    item_type: str  # OTV
    item_id: str
    item_status_label: str  # label renvoyé par le partenaire
    item_generic_status: ItemGenericStatus  # New, Wip, Closed
    item_canal: (
        str | None
    )  # (ex : AMI) Demande de Cécile et Eric (côté partenariats) pour faire des stats
    item_milestone_start_date: (
        datetime.datetime | None
    )  # Date de début de surveillance du logement. Pour afficher dans un agenda. Timezone incluse
    item_milestone_end_date: (
        datetime.datetime | None
    )  # Date de fin de surveillance du logement. Timezone incluse
    item_send_date: datetime.datetime  # Timezone incluse
    item_external_url: str | None  # Lien vers l'item chez le partenaire
    try_push: bool | None = True
    content_title: str
    content_body: str
    content_icon: str | None = (
        "partner_default_icon"  # icône à intégrer dans la liste des notifications. Icône par défaut est l'icône du partenaire
    )
    # Liste des icônes possibles : https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/icone#utilisation-des-icones
