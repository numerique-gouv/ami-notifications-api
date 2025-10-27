import datetime
from typing import Any

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from app import models as m


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


class NotificationCreate(BaseModel):
    user_id: int
    message: str = Field(min_length=1)
    sender: str | None
    title: str | None


class NotificationRead(BaseModel):
    read: bool


class NotificationDTO(SQLAlchemyDTO[m.Notification]):
    config = SQLAlchemyDTOConfig(exclude={"user"})


class RegistrationCreate(BaseModel):
    user_id: int
    subscription: dict[str, Any]


class RegistrationDTO(SQLAlchemyDTO[m.Registration]):
    config = SQLAlchemyDTOConfig(exclude={"user"})
