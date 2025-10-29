import datetime
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
    id: int
    user_id: int
    message: str
    sender: str | None
    title: str | None
    date: datetime.datetime
    unread: bool


class NotificationCreate(BaseModel):
    user_id: int
    message: str = Field(min_length=1)
    sender: str | None
    title: str | None


class NotificationRead(BaseModel):
    read: bool


class Registration(BaseModel):
    id: int
    user_id: int
    subscription: dict[str, Any]
    created_at: datetime.datetime


class RegistrationCreate(BaseModel):
    user_id: int
    subscription: dict[str, Any]
