import datetime

import pytest
from django.core.management import call_command
from django.utils.timezone import now

from ami.notification.models import ScheduledNotification
from ami.user.models import User


@pytest.mark.django_db
def test_command_delete_published_scheduled_notifications(
    user: User,
) -> None:
    scheduled_notification1 = ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference1",
        scheduled_at=now(),
        sent_at=now() - datetime.timedelta(days=6 * 30, minutes=-2),  # too soon
    )
    scheduled_notification2 = ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference2",
        scheduled_at=now(),
        sent_at=None,  # not sent
    )

    ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference3",
        scheduled_at=now(),
        sent_at=now() - datetime.timedelta(days=6 * 30),
    )

    call_command("delete-published-scheduled-notifications")

    all_scheduled_notifications = ScheduledNotification.objects.all()
    assert len(all_scheduled_notifications) == 2
    assert all_scheduled_notifications[0].id == scheduled_notification1.id
    assert all_scheduled_notifications[1].id == scheduled_notification2.id
