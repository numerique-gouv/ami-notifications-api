import urllib.parse

from django.conf import settings
from rest_framework import serializers

from ami.partner.models import Partner


class MobileAppSubscriptionSerializer(serializers.Serializer):
    app_version = serializers.CharField()
    device_id = serializers.CharField()
    fcm_token = serializers.CharField()
    model = serializers.CharField()
    platform = serializers.CharField()


class RegistrationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    subscription = serializers.DictField()
    created_at = serializers.DateTimeField()


class WebPushKeysSerializer(serializers.Serializer):
    auth = serializers.CharField()
    p256dh = serializers.CharField()


class WebPushSubscriptionSerializer(serializers.Serializer):
    endpoint = serializers.URLField()
    keys = WebPushKeysSerializer()


class RegistrationCreateSerializer(serializers.Serializer):
    subscription = serializers.DictField()

    def validate_subscription(self, value):
        endpoint = value.get("endpoint")
        if endpoint:
            endpoint_hostname = urllib.parse.urlparse(endpoint).hostname
            if endpoint_hostname not in settings.PUSH_NOTIFICATIONS_ALLOWED_SERVICES:
                raise serializers.ValidationError(
                    "unknown push notification service",
                    "invalid",
                )
        if "fcm_token" in value:
            s = MobileAppSubscriptionSerializer(data=value)
        else:
            s = WebPushSubscriptionSerializer(data=value)
        s.is_valid(raise_exception=True)
        return s.validated_data


class ConsentResponseSerializer(serializers.Serializer):
    consent_datetime = serializers.DateTimeField(allow_null=True)


class ConsentPostSerializer(serializers.Serializer):
    consent = serializers.BooleanField()


class ConsentPostResponseSerializer(serializers.Serializer):
    message = serializers.ChoiceField(choices=["Consent given", "Consent withdrawn"])


class ConsentSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    partner_id = serializers.CharField(source="partner.slug")
    partner_name = serializers.CharField(source="partner.name")
    consent_datetime = serializers.DateTimeField()


class ConsentUpdateSerializer(serializers.Serializer):
    partner_id = serializers.CharField()
    consent = serializers.BooleanField()

    def validate_partner_id(self, value):
        if value:
            try:
                return Partner.objects.get(slug=value, displayed_on_front=True).id
            except Partner.DoesNotExist:
                raise serializers.ValidationError(
                    "'partner_id' inconnu.",
                    "invalid",
                )
        return None


class RegistrationPutActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["removeFromDeviceId"])


class RegistrationRemoveFromDeviceIdSerializer(serializers.Serializer):
    device_id = serializers.CharField()


class ConsentsUpdateSerializer(serializers.Serializer):
    consent = serializers.BooleanField()


class PersonalDataConsentSerializer(serializers.Serializer):
    consent_datetime = serializers.DateTimeField()


class PersonalDataConsentPostResponseSerializer(serializers.Serializer):
    message = serializers.ChoiceField(
        choices=["Personal data consent given", "Personal data consent withdrawn"]
    )


class PersonalDataConsentUpdateSerializer(serializers.Serializer):
    consent = serializers.BooleanField()


class ApiParticulierCafAdresseSerializer(serializers.Serializer):
    code_postal_ville = serializers.CharField()
    complement_information = serializers.CharField(allow_null=True)
    complement_information_geographique = serializers.CharField(allow_null=True)
    destinataire = serializers.CharField(allow_null=True)
    lieu_dit = serializers.CharField(allow_null=True)
    numero_libelle_voie = serializers.CharField()
    pays = serializers.CharField()


class ApiParticulierCafPersonSerializer(serializers.Serializer):
    date_naissance = serializers.CharField()
    nom_naissance = serializers.CharField()
    nom_usage = serializers.CharField(allow_null=True)
    prenoms = serializers.CharField()
    sexe = serializers.CharField()


class ApiParticulierCafQuotientFamilialSerializer(serializers.Serializer):
    annee = serializers.IntegerField()
    annee_calcul = serializers.IntegerField()
    fournisseur = serializers.CharField()
    mois = serializers.IntegerField()
    mois_calcul = serializers.IntegerField()
    valeur = serializers.IntegerField()


class ApiParticulierCafSerializer(serializers.Serializer):
    adresse = ApiParticulierCafAdresseSerializer(many=False)
    allocataires = serializers.ListField(child=ApiParticulierCafPersonSerializer())
    enfants = serializers.ListField(child=ApiParticulierCafPersonSerializer())
    quotient_familial = ApiParticulierCafQuotientFamilialSerializer()
