from django.conf import settings
from rest_framework import serializers


class TokenSerializer(serializers.Serializer):
    code = serializers.CharField()
    grant_type = serializers.CharField()
    redirect_uri = serializers.CharField()
    client_id = serializers.CharField()
    client_secret = serializers.CharField()

    def validate_grant_type(self, value):
        expected = "authorization_code"
        if value != expected:
            raise serializers.ValidationError(
                f"'grant_type' doit être '{expected}', trouvé '{value}'", "invalid"
            )
        return value

    def validate_redirect_uri(self, value):
        expected = settings.FC_AMI_REDIRECT_URL
        if value != expected:
            raise serializers.ValidationError(
                f"'redirect_uri' doit être '{expected}', trouvé '{value}'",
                "invalid",
            )
        return value

    def validate_client_id(self, value):
        if value != settings.FI_CLIENT_ID:
            raise serializers.ValidationError(
                "'client_id' invalide",
                "invalid",
            )
        return value

    def validate_client_secret(self, value):
        if value != settings.FI_CLIENT_SECRET:
            raise serializers.ValidationError(
                "'client_secret' invalide",
                "invalid",
            )
        return value
