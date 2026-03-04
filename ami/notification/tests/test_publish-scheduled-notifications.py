from typing import Any

import pytest
from django.core.management import call_command


def test_command_publish_scheduled_notifications(monkeypatch: pytest.MonkeyPatch) -> None:
    called = 0

    def fake_handle(*args: Any, **kwargs: Any):
        nonlocal called
        called += 1

    monkeypatch.setattr(
        "ami.notification.management.commands.publish-scheduled-notifications.Command.handle",
        fake_handle,
    )
    call_command("publish-scheduled-notifications")

    assert called == 1
