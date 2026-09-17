import datetime

import pytest
from django.conf import settings
from django.core.management import call_command
from django.utils.timezone import now

from ami.authentication.models import Nonce
from ami.fi.models import FISession
from ami.notification.models import ScheduledNotification
from ami.user.models import User


@pytest.mark.django_db
def test_command_cleanup_expired_fi_sessions() -> None:
    fi_session_1 = FISession.objects.create(user_data={})

    fi_session_2 = FISession.objects.create(user_data={})
    fi_session_2.created_at = now() - datetime.timedelta(seconds=settings.FI_SESSION_AGE - 1)
    fi_session_2.save()

    fi_session_3 = FISession.objects.create(user_data={})
    fi_session_3.created_at = now() - datetime.timedelta(seconds=settings.FI_SESSION_AGE)
    fi_session_3.save()

    call_command("cleanup-db")

    assert FISession.objects.count() == 2
    assert FISession.objects.filter(id=fi_session_1.id).exists() is True
    assert FISession.objects.filter(id=fi_session_2.id).exists() is True
    assert FISession.objects.filter(id=fi_session_3.id).exists() is False


@pytest.mark.django_db
def test_command_cleanup_published_scheduled_notifications(
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

    call_command("cleanup-db")

    all_scheduled_notifications = ScheduledNotification.objects.all()
    assert len(all_scheduled_notifications) == 2
    assert all_scheduled_notifications[0].id == scheduled_notification1.id
    assert all_scheduled_notifications[1].id == scheduled_notification2.id


@pytest.mark.django_db
def test_command_cleanup_expired_nonce() -> None:
    nonce_1 = Nonce.objects.create(nonce="123")

    nonce_2 = Nonce.objects.create(nonce="234")
    nonce_2.created_at = now() - datetime.timedelta(seconds=3555)
    nonce_2.save()

    nonce_3 = Nonce.objects.create(nonce="345")
    nonce_3.created_at = now() - datetime.timedelta(seconds=3605)
    nonce_3.save()

    call_command("cleanup-db")

    assert Nonce.objects.count() == 2
    assert Nonce.objects.filter(id=nonce_1.id).exists() is True
    assert Nonce.objects.filter(id=nonce_2.id).exists() is True
    assert Nonce.objects.filter(id=nonce_3.id).exists() is False
