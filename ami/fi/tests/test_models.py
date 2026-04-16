import datetime

import pytest
from django.conf import settings

from ami.fi.models import FISession


@pytest.mark.django_db
def test_fi_session_is_expired() -> None:
    fi_session = FISession.objects.create(user_data={})
    assert fi_session.is_expired is False
    original_created_at = fi_session.created_at

    fi_session.created_at = original_created_at - datetime.timedelta(
        seconds=settings.FI_SESSION_AGE - 1
    )
    fi_session.save()
    assert fi_session.is_expired is False

    fi_session.created_at = original_created_at - datetime.timedelta(
        seconds=settings.FI_SESSION_AGE
    )
    fi_session.save()
    assert fi_session.is_expired is True
