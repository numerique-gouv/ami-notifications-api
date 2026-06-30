from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .schemas import Followup


class FollowupSerializer(DataclassSerializer):
    class Meta:
        dataclass = Followup


class FollowupItemArchiveSerializer(serializers.Serializer):
    is_archived = serializers.BooleanField()


class FollowupItemArchiveResponse(serializers.Serializer):
    source = serializers.CharField()
    item_external_id = serializers.CharField()
    is_archived = serializers.BooleanField()
