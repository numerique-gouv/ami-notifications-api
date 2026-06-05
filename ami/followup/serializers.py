from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .schemas import FollowUp


class FollowUpSerializer(DataclassSerializer):
    class Meta:
        dataclass = FollowUp


class FollowUpItemArchiveSerializer(serializers.Serializer):
    is_archived = serializers.BooleanField()


class FollowUpItemArchiveResponse(serializers.Serializer):
    inventory = serializers.CharField()
    item_external_id = serializers.CharField()
    is_archived = serializers.BooleanField()
