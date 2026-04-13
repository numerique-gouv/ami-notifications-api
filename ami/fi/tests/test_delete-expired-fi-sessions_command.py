import datetime

import pytest
from django.conf import settings
from django.core.management import call_command
from django.utils.timezone import now

from ami.fi.models import FISession


@pytest.mark.django_db
def test_command_delete_expired_fi_sessions(monkeypatch: pytest.MonkeyPatch) -> None:
    fi_session_1 = FISession.objects.create(user_data={})

    fi_session_2 = FISession.objects.create(user_data={})
    fi_session_2.created_at = now() - datetime.timedelta(seconds=settings.FI_SESSION_AGE - 1)
    fi_session_2.save()

    fi_session_3 = FISession.objects.create(user_data={})
    fi_session_3.created_at = now() - datetime.timedelta(seconds=settings.FI_SESSION_AGE)
    fi_session_3.save()

    call_command("delete-expired-fi-sessions")

    assert FISession.objects.count() == 2
    assert FISession.objects.filter(id=fi_session_1.id).exists() is True
    assert FISession.objects.filter(id=fi_session_2.id).exists() is True
    assert FISession.objects.filter(id=fi_session_3.id).exists() is False
