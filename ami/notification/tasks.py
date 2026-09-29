from django.tasks import task  # type: ignore[import-untyped]

from ami.notification.models import Notification
from ami.notification.push import push


@task
def push_notification(notification_id: str) -> None:
    notification = Notification.objects.get(id=notification_id)
    push(notification)
