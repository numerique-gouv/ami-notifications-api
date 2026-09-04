from rest_framework import serializers


class PartnerGenerateUrlSerializer(serializers.Serializer):
    preferred_username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    address_city = serializers.CharField(required=False)
    address_postcode = serializers.CharField(required=False)
    address_name = serializers.CharField(required=False)


class PartnersResponse(serializers.Serializer):
    slug = serializers.SlugField()
    name = serializers.CharField()
    link = serializers.CharField()
    consent_is_enabled = serializers.BooleanField()
