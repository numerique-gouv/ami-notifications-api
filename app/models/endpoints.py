from datetime import datetime
from typing import Any


class Userinfo:
    aud: str  # "bc3ef03e2748a585005be828f9d1a9719c46df4e728115a106e6c8ee6ddcbacc"
    birthcountry: int  # "99100"
    birthdate: datetime  # "1962-08-24"
    birthplace: int  # "75107"
    email: str  # "wossewodda-3728@yopmail.com"
    exp: str  # 1757583363
    family_name: str  # "DUBOIS"
    gender: str  # "female"
    given_name: str  # "Angela Claire Louise"

    def __init__(self, data: dict[str, Any]) -> None:
        self.aud = data["aud"]
        self.birthcountry = int(data["birthcountry"])
        self.birthdate = datetime.strptime(data["birthdate"], "%Y-%m-%d")
        self.birthplace = int(data["birthplace"])
        self.email = data["email"]
        self.exp = data["exp"]
        self.family_name = data["family_name"]
        self.gender = data["gender"]
        self.given_name = data["given_name"]


class RegistrationCreation:
    subscription: dict[str, Any]
    user_id: str
