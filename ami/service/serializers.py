from rest_framework_dataclasses.serializers import DataclassSerializer

from .schemas import Services


class ServicesSerializer(DataclassSerializer):
    class Meta:
        dataclass = Services
