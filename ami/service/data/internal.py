from ami.service.models import Service
from ami.service.schemas import ServicesItem, ServicesSource, ServicesSourceStatus


def get_internal_data() -> list[ServicesItem]:
    services = Service.objects.all().order_by("title")

    return [service.to_services_item() for service in services]


def get_internal_source() -> ServicesSource:
    source = ServicesSource()

    items = get_internal_data()

    source.items = items
    source.status = ServicesSourceStatus.SUCCESS

    return source
