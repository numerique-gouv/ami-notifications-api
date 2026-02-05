import datetime
import uuid
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field
from webpush import WebPushSubscription


class BaseModel(PydanticBaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True, "use_enum_values": True}


class NotificationEvent(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class ItemGenericStatus(Enum):
    NEW = "new"
    WIP = "wip"
    CLOSED = "closed"


class Notification(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID

    content_title: str
    content_body: str
    content_icon: str | None

    sender: str

    item_type: str | None
    item_id: str | None
    item_status_label: str | None
    item_generic_status: ItemGenericStatus | None
    item_canal: str | None
    item_milestone_start_date: datetime.datetime | None
    item_milestone_end_date: datetime.datetime | None
    item_external_url: str | None

    created_at: datetime.datetime

    read: bool


class NotificationCreate(BaseModel):
    recipient_fc_hash: str = Field(
        description="Hash de la concaténation des données pivot FC de l'usager destinataire, cf doc",
    )

    content_title: str = Field(min_length=1, description="Titre de la notification")
    content_body: str = Field(min_length=1, description="Contenu de la notification")
    content_icon: str | None = Field(
        min_length=1,
        default=None,
        description="Nom technique de l'icône à associer à la notification dans l'application AMI, "
        "à choisir dans [les icones du DSFR](https://www.systeme-de-design.gouv.fr/version-courante/fr/fondamentaux/icone).",
    )

    item_type: str = Field(
        min_length=1,
        description="Champ libre représentant le type de l'objet associé à la notification, "
        'par exemple : "OTV" dans le cas des démarches "Opération Tranquillité Vacances"',
    )
    item_id: str = Field(
        min_length=1,
        description="Identifiant dans le référentiel partenaire de l'objet associé à la notification",
    )
    item_status_label: str = Field(
        min_length=1,
        description='Champ libre représentant le statut de l\'objet associé à la notification, par exemple : "Brouillon"',
    )
    item_generic_status: ItemGenericStatus = Field(
        description="Statut générique de l'objet associé à la notification pilotant des comportements spécifiques dans l'application AMI"
    )
    item_canal: str | None = Field(
        min_length=1,
        default=None,
        description="Canal source de l'objet associé à la notification (AMI, PSL, etc.) pour la mesure d'impact",
    )
    item_milestone_start_date: datetime.datetime | None = Field(
        default=None,
        description="Date (au format ISO 8601) de début de la période correspondant à l'objet associé à la notification, "
        "ex : date de début de surveillance du logement dans le cadre d'une OTV",
    )
    item_milestone_end_date: datetime.datetime | None = Field(
        default=None,
        description="Date (au format ISO 8601) de fin de la période correspondant à l'objet associé à la notification, "
        "ex : date de fin de surveillance du logement dans le cadre d'une OTV",
    )
    item_external_url: str | None = Field(
        min_length=1,
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


class NotificationResponse(BaseModel):
    notification_id: uuid.UUID
    notification_send_status: bool


class NotificationRead(BaseModel):
    read: bool


class NotificationPush(BaseModel):
    title: str
    message: str
    content_icon: str | None
    sender: str


class AdminNotificationCreate(BaseModel):
    user_id: uuid.UUID
    content_title: str = Field(min_length=1, alias="title")
    content_body: str = Field(min_length=1, alias="message")
    sender: str = Field(min_length=1)


class NotificationLegacy(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str = Field(alias="content_title")
    message: str = Field(alias="content_body")
    sender: str
    read: bool
    created_at: datetime.datetime


class ScheduledNotificationCreate(BaseModel):
    content_title: str = Field(min_length=1)
    content_body: str = Field(min_length=1)
    content_icon: str = Field(min_length=1)
    reference: str = Field(min_length=1)
    scheduled_at: datetime.datetime


class ScheduledNotificationResponse(BaseModel):
    scheduled_notification_id: uuid.UUID


class MobileAppSubscription(BaseModel):
    app_version: str
    device_id: str
    fcm_token: str
    model: str
    platform: str


class Registration(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    subscription: MobileAppSubscription | WebPushSubscription
    created_at: datetime.datetime


class RegistrationCreate(BaseModel):
    subscription: MobileAppSubscription | WebPushSubscription


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


@dataclass
class Agenda:
    school_holidays: AgendaCatalog | None = field(default_factory=AgendaCatalog)
    public_holidays: AgendaCatalog | None = field(default_factory=AgendaCatalog)
    elections: AgendaCatalog | None = field(default_factory=AgendaCatalog)
