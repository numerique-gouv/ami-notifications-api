from asgiref.sync import async_to_sync
from django.tasks import task  # type: ignore[import-untyped]

from ami.notification.models import Notification
from ami.notification.push import push


@task
def push_notification(notification_id: str, try_push: bool) -> None:
    notification = Notification.objects.get(id=notification_id)
    async_to_sync(push)(notification, try_push)
