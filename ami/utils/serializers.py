from rest_framework import serializers


class RecipientFcHashSerializer(serializers.Serializer):
    given_name = serializers.CharField()
    family_name = serializers.CharField()
    birthdate = serializers.CharField()
    gender = serializers.CharField()
    birthplace = serializers.CharField(required=False)
    birthcountry = serializers.CharField()
