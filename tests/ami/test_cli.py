import csv
from pathlib import Path
from typing import Any, Dict, List

import pytest
from click.testing import CliRunner
from freezegun import freeze_time
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


@freeze_time("2026-01-23 10:36:00")
def test_cli_generate_identity_tokens(
    runner: CliRunner,
    root_command: LitestarExtensionGroup,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    csv_content = (
        "id,fc_hash,preferred_username,email,address_city,address_postcode,address_name\n"
        "1,4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060,,"
        "wossewodda-3728@yopmail.com,Paris,75007,20 Avenue de Ségur\n"
    )
    input_csv_file_path = tmp_path / "input_file_test_cli.csv"
    input_csv_file_path.write_text(csv_content, encoding="utf-8")
    output_csv_file_path = tmp_path / "output_file_test_cli.csv"
    output_csv_file_path.write_text("", encoding="utf-8")

    def mock_generate_identity_token(**kwargs: Any):
        return "fake-identity-token"

    monkeypatch.setattr("app.utils.generate_identity_token", mock_generate_identity_token)

    result = runner.invoke(
        root_command,
        [
            "generate-identity-tokens",
            str(tmp_path / "input_file_test_cli.csv"),
            str(tmp_path / "output_file_test_cli.csv"),
        ],
    )

    assert not result.exception

    input_fieldnames = [
        "id",
        "preferred_username",
        "email",
        "address_city",
        "address_postcode",
        "address_name",
        "fc_hash",
    ]
    output_fieldnames = input_fieldnames + ["identity_token"]

    input_data = get_data_from_file(str(tmp_path / "input_file_test_cli.csv"), input_fieldnames)
    output_data = get_data_from_file(str(tmp_path / "output_file_test_cli.csv"), output_fieldnames)

    assert input_data[0]["id"] == output_data[0]["id"]
    assert input_data[0]["preferred_username"] == output_data[0]["preferred_username"]
    assert input_data[0]["email"] == output_data[0]["email"]
    assert input_data[0]["address_city"] == output_data[0]["address_city"]
    assert input_data[0]["address_postcode"] == output_data[0]["address_postcode"]
    assert input_data[0]["address_name"] == output_data[0]["address_name"]
    assert input_data[0]["fc_hash"] == output_data[0]["fc_hash"]
    assert output_data[0]["identity_token"] is not None


def get_data_from_file(
    file_path: str,
    fieldnames: List[str],
) -> List[Any]:
    results: List[Dict[str, str]] = []

    with open(file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row in csv_reader:
            new_line: Dict[str, str] = {}
            for fieldname in fieldnames:
                new_line[fieldname] = row[fieldname]

            results.append(new_line)

    return results
