from rest_framework_dataclasses.serializers import DataclassSerializer

from .schemas import Catalog


class CatalogSerializer(DataclassSerializer):
    class Meta:
        dataclass = Catalog
