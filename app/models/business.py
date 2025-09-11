from datetime import datetime
from typing import Any


class User:
    id: int
    email: str
    given_names: list[str]
    family_name: str  #
    birthdate: datetime  # (format YYY-MM-DD)
    gender: str  # (male / female)
    birthplace: int  # (code INSEE du lieu de naissance sur 5 chiffres)
    birthcountry: int  # (code INSEE du pays sur 5 chiffres)
    # messages: list["Messages"]
    registrations: list["Registration"]
    # notifications: list["Notification"]


class Message:
    id: int
    date: datetime
    user: User
    body: str
    sender: str
    title: str


class Registration:
    id: int
    user: User
    subscription: dict[str, Any]
    label: str
    enabled: bool
    created_at: datetime
