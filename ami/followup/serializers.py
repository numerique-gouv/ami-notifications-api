from rest_framework_dataclasses.serializers import DataclassSerializer

from .schemas import FollowUp


class FollowUpSerializer(DataclassSerializer):
    class Meta:
        dataclass = FollowUp
