from typing import Any

import pytest
from django.core.management import call_command


def test_command_delete_published_scheduled_notifications(monkeypatch: pytest.MonkeyPatch) -> None:
    called = 0

    def fake_handle(*args: Any, **kwargs: Any):
        nonlocal called
        called += 1

    monkeypatch.setattr(
        "ami.notification.management.commands.delete-published-scheduled-notifications.Command.handle",
        fake_handle,
    )
    call_command("delete-published-scheduled-notifications")

    assert called == 1
