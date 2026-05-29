from importlib.metadata import version

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


def test_parse_accepts_spaced_trailing_interface_placeholder() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show mac address-table notification change interface HundredGigE 2/0/25",
        raw_output="MAC Notification Feature is Disabled on the switch\n"
        "HundredGigE2/0/25 Disabled Disabled",
    )

    assert parsed["interface"] == "HundredGigE2/0/25"


def test_parse_accepts_interface_status_command() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show interfaces status",
        raw_output="Gi1/2 Uplink connected 125 full 100 10/100/1000-TX",
    )

    assert parsed["interfaces"]["GigabitEthernet1/2"]["status"] == "connected"


def test_parse_accepts_spaced_pipe_include_placeholder() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show interfaces | include GigabitEthernet1 is up",
        raw_output="GigabitEthernet1 is up, line protocol is up (connected)",
    )

    assert parsed["GigabitEthernet1"]["connected"] is True


def test_supported_commands_includes_converted_upstream_files() -> None:
    commands = set(yenie_parser.supported_commands("iosxe"))

    assert "show device-tracking database" in commands
    assert "show authentication sessions" in commands
    assert "authentication display config-mode" in commands
    assert "show inventory raw" in commands
    assert "show cdp neighbors" in commands
    assert "show arp" in commands
    assert "show mac address-table" in commands
    assert "show interfaces status" in commands
    assert "show ip interface brief | include {ip}" in commands
    assert "show run policy-map {name}" in commands
    assert "show running-config | section bgp" in commands
    assert "show running-config vrf" in commands


def test_package_version_comes_from_project_metadata() -> None:
    assert yenie_parser.__version__ == version("yenie-parser")
