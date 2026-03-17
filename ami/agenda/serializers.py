from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from ami.agenda.schemas import Agenda


class AgendaQueryParamsSerializer(serializers.Serializer):
    current_date = serializers.DateField()
    filter_items = serializers.ListField(child=serializers.CharField(), required=False)

    def to_internal_value(self, data):
        data = data.copy()
        if "filter-items" in data:
            data.setlist("filter_items", data.getlist("filter-items"))
        return super().to_internal_value(data)


class AgendaSerializer(DataclassSerializer):
    class Meta:
        dataclass = Agenda
