import datetime
import uuid
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
    user_id: uuid.UUID
    subscription: dict[str, Any]
