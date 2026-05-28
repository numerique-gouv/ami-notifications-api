from dataclasses import dataclass
from typing import Self

from django.conf import settings


@dataclass
class DataProvider:
    id: str
    label: str
    scope: str
    url: str

    @classmethod
    def from_settings(cls) -> dict[str, Self]:
        result = {}
        for key, label in settings.FC_DATA_PROVIDERS.items():
            base_url = getattr(settings, f"{key}_base_url".upper())
            endpoint = getattr(settings, f"{key}_endpoint".upper())
            scope = getattr(settings, f"{key}_scope".upper())
            result[key] = cls(
                key,
                label,
                scope,
                f"{base_url}{endpoint}",
            )
        return result

    def is_enabled(self):
        return getattr(settings, f"{self.id}_enabled".upper())


data_providers = DataProvider.from_settings()
