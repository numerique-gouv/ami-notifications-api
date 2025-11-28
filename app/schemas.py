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


class Notification(BaseModel):
    recipient_fc_hash: str = Field(
        description="Hash de la concaténation des données pivot FC de l'usager destinataire, cf doc"
    )
    # Dans AMI, on stocke la liste des partenaires et leur clé d'API (en base ou en variables d'env)
    # Dans la table Notifications, il y a le partenaire émetteur
    item_type: str = Field(
        description='Champ libre représentant le type de l\'objet associé à la notification, par exemple : "OTV" dans le cas des démarches "Opération Tranquillité Vacances"'
    )
    item_id: str = Field(
        description="Identifiant dans le référentiel partenaire de l'objet associé à la notification"
    )
    item_status_label: str = Field(
        description='Champ libre représentant le statut de l\'objet associé à la notification, par exemple : "Brouillon"'
    )
    item_generic_status: ItemGenericStatus = Field(
        description="Statut générique de l'objet associé à la notification pilotant des comportements spécifiques dans l'application AMI"
    )
    item_canal: str | None = Field(
        default=None,
        description="Canal source de l'objet associé à la notification (AMI, PSL, etc.) pour la mesure d'impact",
    )
    item_milestone_start_date: datetime.datetime | None = Field(
        default=None,
        description="Date (au format ISO 8601) de début de la période correspondant à l'objet associé à la notification, ex : date de début de surveillance du logement dans le cadre d'une OTV",
    )
    item_milestone_end_date: datetime.datetime | None = Field(
        default=None,
        description="Date (au format ISO 8601) de fin de la période correspondant à l'objet associé à la notification, ex : date de fin de surveillance du logement dans le cadre d'une OTV",
    )
    item_external_url: str | None = Field(
        default=None,
        description="Lien vers le portail du partenaire de l'objet associé à la notification",
    )
    send_date: datetime.datetime = Field(
        description="Date (au format ISO 8601) d'émission de la notification côté partenaire"
    )
    try_push: bool | None = Field(
        default=True,
        description="Indique si le système doit essayer de déclencher une Notification Push sur les terminaux de l'usager",
    )
    content_title: str = Field(description="Titre de la notification")
    content_body: str = Field(description="Contenu de la notification")
    content_icon: str | None = Field(
        default="otv_default_icon",
        description="Nom technique de l'icône à associer à la notification dans l'application AMI, à choisir dans https://remixicon.com/",
    )


class NotifyResponse(BaseModel):
    notification_id: uuid.UUID
    notification_send_status: bool
