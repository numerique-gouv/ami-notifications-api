import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from django.http import HttpRequest
from drf_spectacular.generators import SchemaGenerator


class TimeUnit(str, Enum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"


@dataclass
class ExpirationRule(ABC):
    @abstractmethod
    def compute_expires_at(self) -> datetime.datetime:
        pass


@dataclass
class DurationExpiration(ExpirationRule):
    amount: int
    unit: TimeUnit

    def __init__(self, amount: int, unit: TimeUnit):
        super().__init__()
        self.amount = amount
        self.unit = unit

    def compute_expires_at(self) -> datetime.datetime:
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = datetime.timedelta(**{self.unit.value: self.amount})
        return now + delta


@dataclass
class MonthlyExpiration(ExpirationRule):
    def compute_expires_at(self) -> datetime.datetime:
        now = datetime.datetime.now(datetime.timezone.utc)
        try:
            return datetime.datetime(
                year=now.year, month=now.month + 1, day=1, tzinfo=datetime.timezone.utc
            )
        except ValueError:
            return datetime.datetime(
                year=now.year + 1, month=1, day=1, tzinfo=datetime.timezone.utc
            )


def custom_postprocessing_hook(
    result: Dict[str, Any],
    generator: "SchemaGenerator",
    request: Optional["HttpRequest"],
    public: bool,
) -> Dict[str, Any]:
    def is_partner_api(path: str) -> bool:
        return any(
            x for x in result["paths"][path].values() if "API partenaires" in (x.get("tags") or [])
        )

    if request and request.path == "/schema/internal-apis":
        result["info"]["title"] = "AMI - Internal APIs"
        result["paths"] = {x: y for x, y in result["paths"].items() if not is_partner_api(x)}
    else:
        result["paths"] = {x: y for x, y in result["paths"].items() if is_partner_api(x)}

    return result
