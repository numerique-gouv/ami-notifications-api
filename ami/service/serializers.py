from django.conf import settings
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from ami.utils import generate_identity_token

from ..user.models import PersonalDataConsent
from .schemas import Services


class ServicesSerializer(DataclassSerializer):
    class Meta:
        dataclass = Services


class OTVJWTTokenSerializer(serializers.Serializer):
    preferred_username = serializers.CharField(allow_blank=True, required=False, default="")
    email = serializers.CharField(allow_blank=True, required=False, default="")
    address_city = serializers.CharField(allow_blank=True, required=False, default="")
    address_postcode = serializers.CharField(allow_blank=True, required=False, default="")
    address_citycode = serializers.CharField(allow_blank=True, required=False, default="")
    address_name = serializers.CharField(allow_blank=True, required=False, default="")

    @classmethod
    def get_parameter_value(cls, *, validated_data, user):
        preferred_username = ""
        email = ""
        address_city = ""
        address_postcode = ""
        address_citycode = ""
        address_name = ""

        try:
            personal_data_consent: PersonalDataConsent = user.personaldataconsent
        except PersonalDataConsent.DoesNotExist:
            personal_data_consent: PersonalDataConsent = PersonalDataConsent()

        if personal_data_consent.consent_datetime:
            preferred_username = validated_data["preferred_username"]
            email = validated_data["email"]
            address_city = validated_data["address_city"]
            address_postcode = validated_data["address_postcode"]
            address_citycode = validated_data["address_citycode"]
            address_name = validated_data["address_name"]

        otv_private_key = settings.PARTNERS_PSL_OTV_JWT_CERT_PFX_B64
        psl_otv_public_key = settings.PARTNERS_PSL_OTV_JWE_PUBLIC_KEY
        if otv_private_key and psl_otv_public_key:
            return generate_identity_token(
                preferred_username,
                email,
                address_city,
                address_postcode,
                address_citycode,
                address_name,
                user.fc_hash,
            )
        return ""


PARAMETER_SERIALIZERS = {
    "otv_jwt_token": OTVJWTTokenSerializer,
}


class ParameterSerializer(serializers.Serializer):
    parameter = serializers.ChoiceField(choices=list(PARAMETER_SERIALIZERS.keys()))
    values = serializers.DictField()

    def validate(self, attrs):
        data_serializer = PARAMETER_SERIALIZERS[attrs["parameter"]](data=attrs["values"])
        data_serializer.is_valid(raise_exception=True)

        attrs["values"] = data_serializer.validated_data
        return attrs


class ServicesItemsParametersSerializer(serializers.Serializer):
    parameters = ParameterSerializer(many=True, required=False)


def get_parameters_values(*, validated_data, user):
    values = {}
    for value in validated_data.get("parameters") or []:
        data_serializer_class = PARAMETER_SERIALIZERS[value["parameter"]]
        values[value["parameter"]] = data_serializer_class.get_parameter_value(
            validated_data=value["values"], user=user
        )
    return values
