import pytest

import yenie_parser
from yenie_parser import UnsupportedCommandError, UnsupportedPlatformError


def test_parse_dispatches_with_case_and_whitespace_normalization() -> None:
    output = "Binding Table has 1 entries, 0 dynamic (limit 200000)"

    parsed = yenie_parser.parse(
        platform=" IOSXE ",
        command=" SHOW   DEVICE-TRACKING   DATABASE ",
        raw_output=output,
    )

    assert parsed["binding_table_count"] == 1
    assert parsed["binding_table_limit"] == 200000


def test_parse_preserves_hyphenated_command_tokens() -> None:
    with pytest.raises(UnsupportedCommandError):
        yenie_parser.parse(
            platform="iosxe",
            command="show device tracking database",
            raw_output="Binding Table has 1 entries, 0 dynamic (limit 200000)",
        )


def test_parse_raises_for_unsupported_platform() -> None:
    with pytest.raises(UnsupportedPlatformError):
        yenie_parser.parse(platform="nxos", command="show version", raw_output="")


def test_parse_raises_for_unsupported_command() -> None:
    with pytest.raises(UnsupportedCommandError):
        yenie_parser.parse(platform="iosxe", command="show version", raw_output="")


def test_parse_accepts_concrete_placeholder_values() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show device-tracking counters interface Gi1/0/1",
        raw_output="Received messages on Gi1/0/1:\nNDP RS[1] NS[2]",
    )

    assert parsed["interface"]["GigabitEthernet1/0/1"]["message_type"]["received"]["protocols"][
        "ndp"
    ] == {"rs": 1, "ns": 2}


def test_parse_accepts_registered_template_string() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show device-tracking database vlan {vlan_id}",
        raw_output="Binding Table has 1 entries, 0 dynamic (limit 200000)",
    )

    assert parsed["dynamic_entry_count"] == 0


def test_parse_accepts_quoted_placeholder_values() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command='show inventory "Chassis"',
        raw_output='NAME: "Chassis", DESCR: "Cisco Catalyst Chassis"',
    )

    assert parsed["name"]["Chassis"]["description"] == "Cisco Catalyst Chassis"


def test_supported_commands_includes_both_upstream_files() -> None:
    commands = set(yenie_parser.supported_commands("iosxe"))

    assert "show device-tracking database" in commands
    assert "show authentication sessions" in commands
    assert "authentication display config-mode" in commands
    assert "show inventory raw" in commands
    assert "show cdp neighbors" in commands
