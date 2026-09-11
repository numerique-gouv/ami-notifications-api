from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from ami.partner.schemas import PartnersSource


class PartnerGenerateUrlSerializer(serializers.Serializer):
    preferred_username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    address_city = serializers.CharField(required=False)
    address_postcode = serializers.CharField(required=False)
    address_name = serializers.CharField(required=False)


class PartnersSerializer(DataclassSerializer):
    class Meta:
        dataclass = PartnersSource
