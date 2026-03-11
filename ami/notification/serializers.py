from rest_framework import serializers


class NotificationResponseSerializer(serializers.Serializer):
    notification_id = serializers.UUIDField()
    notification_send_status = serializers.BooleanField()


class AdminNotificationCreateSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    title = serializers.CharField(min_length=1, source="content_title")
    message = serializers.CharField(min_length=1, source="content_body")
    sender = serializers.CharField(min_length=1)
