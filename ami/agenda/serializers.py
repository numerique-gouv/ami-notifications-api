from rest_framework import serializers


class AgendaQueryParamsSerializer(serializers.Serializer):
    current_date = serializers.DateField()
    filter_items = serializers.ListField(child=serializers.CharField(), required=False)

    def to_internal_value(self, data):
        data = data.copy()
        if "filter-items" in data:
            data.setlist("filter_items", data.getlist("filter-items"))
        return super().to_internal_value(data)


class AgendaCatalogItemSerializer(serializers.Serializer):
    kind = serializers.SerializerMethodField()
    title = serializers.CharField()
    description = serializers.CharField()
    date = serializers.DateField(default=None)
    start_date = serializers.DateField(default=None)
    end_date = serializers.DateField(default=None)
    zones = serializers.CharField()
    emoji = serializers.CharField()

    def get_kind(self, obj):
        return obj.kind.value


class AgendaCatalogSerializer(serializers.Serializer):
    status = serializers.SerializerMethodField()
    items = AgendaCatalogItemSerializer(many=True)
    expires_at = serializers.DateTimeField(default=None)

    def get_status(self, obj):
        return obj.status.value


class AgendaSerializer(serializers.Serializer):
    school_holidays = AgendaCatalogSerializer(default=None)
    public_holidays = AgendaCatalogSerializer(default=None)
    elections = AgendaCatalogSerializer(default=None)


class FollowUpInventoryItemSerializer(serializers.Serializer):
    external_id = serializers.CharField()
    kind = serializers.SerializerMethodField()
    status_id = serializers.SerializerMethodField()
    status_label = serializers.CharField()
    milestone_start_date = serializers.DateTimeField(default=None)
    milestone_end_date = serializers.DateTimeField(default=None)
    title = serializers.CharField()
    description = serializers.CharField()
    external_url = serializers.URLField(default=None)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_kind(self, obj):
        return obj.kind.value

    def get_status_id(self, obj):
        return obj.status_id.value


class FollowUpInventorySerializer(serializers.Serializer):
    status = serializers.SerializerMethodField()
    items = FollowUpInventoryItemSerializer(many=True)

    def get_status(self, obj):
        return obj.status.value


class FollowUpSerializer(serializers.Serializer):
    psl = FollowUpInventorySerializer(default=None)
