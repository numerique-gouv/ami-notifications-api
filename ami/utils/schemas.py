import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


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
