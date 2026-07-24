from ami.service.models import Service
from ami.service.schemas import ServicesItem, ServicesSource, ServicesSourceStatus
from ami.user.models import User


def get_internal_data(*, current_user: User) -> list[ServicesItem]:
    services = Service.objects.all().order_by("title")

    return [
        service.to_services_item() for service in services if service.accessible_to(current_user)
    ]


def get_internal_source(*, current_user: User) -> ServicesSource:
    source = ServicesSource()

    items = get_internal_data(current_user=current_user)

    source.items = items
    source.status = ServicesSourceStatus.SUCCESS

    return source
