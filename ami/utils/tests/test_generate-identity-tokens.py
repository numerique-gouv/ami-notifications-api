from typing import Any

import pytest
from django.core.management import call_command


def test_command_generate_identity_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    called = 0

    def fake_handle(*args: Any, **kwargs: Any):
        nonlocal called
        called += 1

    monkeypatch.setattr(
        "ami.utils.management.commands.generate-identity-tokens.Command.handle",
        fake_handle,
    )
    call_command("generate-identity-tokens", "input_file_test_cli.csv", "output_file_test_cli.csv")

    assert called == 1
