from typing import Any

import pytest
from click.testing import CliRunner
from litestar.cli._utils import LitestarExtensionGroup


def test_cli_publish_scheduled_notifications(
    runner: CliRunner,
    root_command: LitestarExtensionGroup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = 0

    async def fake_publish(*args: Any):
        nonlocal called
        called += 1

    monkeypatch.setattr(
        "app.cli.ScheduledNotificationService.publish_scheduled_notifications", fake_publish
    )
    result = runner.invoke(root_command, ["publish-scheduled-notifications"])

    assert not result.exception
    assert called == 1


def test_cli_delete_published_scheduled_notifications(
    runner: CliRunner,
    root_command: LitestarExtensionGroup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = 0

    async def fake_delete_published(*args: Any):
        nonlocal called
        called += 1

    monkeypatch.setattr(
        "app.cli.ScheduledNotificationService.delete_published_scheduled_notifications",
        fake_delete_published,
    )
    result = runner.invoke(root_command, ["delete-published-scheduled-notifications"])

    assert not result.exception
    assert called == 1
