from asgiref.sync import async_to_sync
from django.tasks import Task, task  # type: ignore[import-untyped]

from ami.notification.models import Notification
from ami.notification.push import push


def _push_notification(notification_id: str, try_push: bool) -> None:
    notification = Notification.objects.get(id=notification_id)
    async_to_sync(push)(notification, try_push)


# Using the @task decorator makes pyright complain, so we do it this way with explicit type annotation
push_notification: Task = task(_push_notification)
