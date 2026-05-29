from pathlib import Path

from click.testing import CliRunner

import yenie_parser
from yenie_parser._cli import main


RAW_DEVICE_TRACKING_OUTPUT = "Binding Table has 1 entries, 0 dynamic (limit 200000)"


def test_cli_without_command_shows_help() -> None:
    result = CliRunner().invoke(main)

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "parse" in result.output
    assert "list" in result.output


def test_cli_version_prints_project_metadata() -> None:
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "yenie-parser" in result.output
    assert yenie_parser.__version__ in result.output
    assert "Small, standalone Cisco CLI parsers" in result.output
    assert "click" in result.output
    assert "rich" in result.output


def test_cli_parse_prints_rich_pretty_result_from_raw_output() -> None:
    result = CliRunner().invoke(
        main,
        [
            "parse",
            "--platform",
            "iosxe",
            "--command",
            "show device-tracking database",
            "--raw-output",
            RAW_DEVICE_TRACKING_OUTPUT,
        ],
    )

    assert result.exit_code == 0
    assert "'binding_table_count': 1" in result.output
    assert "'binding_table_limit': 200000" in result.output


def test_cli_parse_accepts_stdin() -> None:
    result = CliRunner().invoke(
        main,
        [
            "parse",
            "--platform",
            "iosxe",
            "--command",
            "show device-tracking database",
        ],
        input=RAW_DEVICE_TRACKING_OUTPUT,
    )

    assert result.exit_code == 0
    assert "'dynamic_entry_count': 0" in result.output


def test_cli_parse_accepts_raw_file(tmp_path: Path) -> None:
    raw_file = tmp_path / "raw-output.txt"
    raw_file.write_text(RAW_DEVICE_TRACKING_OUTPUT)

    result = CliRunner().invoke(
        main,
        [
            "parse",
            "--platform",
            "iosxe",
            "--command",
            "show device-tracking database",
            "--raw-file",
            str(raw_file),
        ],
    )

    assert result.exit_code == 0
    assert "'binding_table_limit': 200000" in result.output


def test_cli_parse_strict_exits_nonzero_for_unsupported_command() -> None:
    result = CliRunner().invoke(
        main,
        [
            "parse",
            "--platform",
            "iosxe",
            "--command",
            "show version",
            "--raw-output",
            "raw output",
            "-s",
        ],
    )

    assert result.exit_code == 1
    assert "Unsupported command for iosxe" in result.output


def test_cli_list_prints_supported_commands_with_filenames() -> None:
    result = CliRunner().invoke(main, ["list"])

    assert result.exit_code == 0
    assert "show authentication sessions" in result.output
    assert "_genie_show_authentication_sessions.py" in result.output


def test_cli_list_searches_with_positional_query() -> None:
    result = CliRunner().invoke(main, ["list", "authentication s"])

    assert result.exit_code == 0
    assert "show authentication sessions" in result.output
    assert "_genie_show_authentication_sessions.py" in result.output


def test_cli_list_searches_with_search_option() -> None:
    result = CliRunner().invoke(main, ["list", "--search", "authentication s"])

    assert result.exit_code == 0
    assert "show authentication sessions" in result.output
    assert "_genie_show_authentication_sessions.py" in result.output


def test_cli_list_matches_command_with_registry_rules() -> None:
    result = CliRunner().invoke(main, ["list", "--command", "show authentication sessions"])

    assert result.exit_code == 0
    assert "show authentication sessions" in result.output
    assert "_genie_show_authentication_sessions.py" in result.output
