import datetime
from typing import Any


class Userinfo:
    aud: str
    birthcountry: int
    birthdate: datetime.date
    birthplace: int
    email: str
    exp: str
    family_name: str
    gender: str
    given_name: str

    def __init__(self, data: dict[str, Any]) -> None:
        self.aud = data["aud"]
        self.birthcountry = int(data["birthcountry"])
        self.birthdate = datetime.datetime.strptime(data["birthdate"], "%Y-%m-%d").date()
        self.birthplace = int(data["birthplace"])
        self.email = data["email"]
        self.exp = data["exp"]
        self.family_name = data["family_name"]
        self.gender = data["gender"]
        self.given_name = data["given_name"]
