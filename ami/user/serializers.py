from rest_framework import serializers


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
        if "fcm_token" in value:
            s = MobileAppSubscriptionSerializer(data=value)
        else:
            s = WebPushSubscriptionSerializer(data=value)
        s.is_valid(raise_exception=True)
        return s.validated_data
