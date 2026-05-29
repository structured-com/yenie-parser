from importlib.metadata import version

import pytest

import yenie_parser
from yenie_parser import (
    ParserExecutionError,
    UnparsedOutputError,
    UnsupportedCommandError,
    UnsupportedPlatformError,
)
from yenie_parser import _registry as registry


def test_parse_dispatches_with_case_and_whitespace_normalization() -> None:
    output = "Binding Table has 1 entries, 0 dynamic (limit 200000)"

    parsed = yenie_parser.parse(
        platform=" IOSXE ",
        command=" SHOW   DEVICE-TRACKING   DATABASE ",
        raw_output=output,
    )

    assert parsed["binding_table_count"] == 1
    assert parsed["binding_table_limit"] == 200000


def test_parse_returns_none_for_unsupported_command_by_default() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show device tracking database",
        raw_output="Binding Table has 1 entries, 0 dynamic (limit 200000)",
    )

    assert parsed is None


def test_parse_returns_none_for_unsupported_platform_by_default() -> None:
    assert yenie_parser.parse(platform="nxos", command="show version", raw_output="") is None


def test_parse_strict_raises_for_unsupported_platform() -> None:
    with pytest.raises(UnsupportedPlatformError):
        yenie_parser.parse(platform="nxos", command="show version", raw_output="", strict=True)


def test_parse_strict_raises_for_unsupported_command() -> None:
    with pytest.raises(UnsupportedCommandError):
        yenie_parser.parse(platform="iosxe", command="show version", raw_output="", strict=True)


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


def test_parse_returns_none_for_unparsed_output_by_default() -> None:
    assert (
        yenie_parser.parse(
            platform="iosxe",
            command="show device-tracking database",
            raw_output="not device tracking output",
        )
        is None
    )


def test_parse_on_failure_empty_dict_returns_empty_dict() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show version",
        raw_output="raw output",
        on_failure="empty_dict",
    )

    assert parsed == {}


def test_parse_on_failure_raw_output_returns_original_output() -> None:
    raw_output = "raw output\nwith exact content"

    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show version",
        raw_output=raw_output,
        on_failure="raw_output",
    )

    assert parsed is raw_output


def test_parse_strict_overrides_on_failure() -> None:
    with pytest.raises(UnsupportedCommandError):
        yenie_parser.parse(
            platform="iosxe",
            command="show version",
            raw_output="raw output",
            strict=True,
            on_failure="raw_output",
        )


@pytest.mark.parametrize(
    ("on_failure", "expected"),
    [
        ("none", None),
        ("empty_dict", {}),
        ("raw_output", "raw output"),
    ],
)
def test_parse_warns_and_returns_configured_fallback(
    on_failure: registry.OnFailure, expected: object
) -> None:
    with pytest.warns(yenie_parser.YenieParserWarning, match="Unsupported command"):
        parsed = yenie_parser.parse(
            platform="iosxe",
            command="show version",
            raw_output="raw output",
            warn=True,
            on_failure=on_failure,
        )

    assert parsed == expected


def test_parse_warns_before_strict_exception() -> None:
    with pytest.warns(yenie_parser.YenieParserWarning, match="Unsupported command"):
        with pytest.raises(UnsupportedCommandError):
            yenie_parser.parse(
                platform="iosxe",
                command="show version",
                raw_output="raw output",
                strict=True,
                warn=True,
            )


def test_parse_raises_value_error_for_invalid_on_failure() -> None:
    with pytest.raises(ValueError, match="Invalid on_failure value"):
        yenie_parser.parse(
            platform="nxos",
            command="show version",
            raw_output="",
            strict=True,
            on_failure="invalid",
        )


def test_parse_strict_raises_for_unparsed_output() -> None:
    with pytest.raises(UnparsedOutputError):
        yenie_parser.parse(
            platform="iosxe",
            command="show device-tracking database",
            raw_output="not device tracking output",
            strict=True,
        )


def test_parse_strict_raises_parser_execution_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class BrokenParser:
        def cli(self, output: str | None = None) -> dict:
            raise RuntimeError("boom")

    monkeypatch.setattr(
        registry,
        "_load_iosxe_registry",
        lambda: (
            registry.ParserEntry(
                platform="iosxe",
                template="show broken",
                parser_class=BrokenParser,
                source_order=1,
            ),
        ),
    )

    with pytest.raises(ParserExecutionError) as exc_info:
        yenie_parser.parse(
            platform="iosxe",
            command="show broken",
            raw_output="raw output",
            strict=True,
        )

    assert isinstance(exc_info.value.__cause__, RuntimeError)


def test_parse_handles_ambiguous_command(monkeypatch: pytest.MonkeyPatch) -> None:
    class ParserA:
        def cli(self, output: str | None = None) -> dict:
            return {"parser": "a"}

    class ParserB:
        def cli(self, output: str | None = None) -> dict:
            return {"parser": "b"}

    monkeypatch.setattr(
        registry,
        "_load_iosxe_registry",
        lambda: (
            registry.ParserEntry(
                platform="iosxe",
                template="show fake {value}",
                parser_class=ParserA,
                source_order=1,
            ),
            registry.ParserEntry(
                platform="iosxe",
                template="show fake {item}",
                parser_class=ParserB,
                source_order=1,
            ),
        ),
    )

    assert (
        yenie_parser.parse(platform="iosxe", command="show fake thing", raw_output="raw output")
        is None
    )

    with pytest.raises(yenie_parser.AmbiguousCommandError):
        yenie_parser.parse(
            platform="iosxe",
            command="show fake thing",
            raw_output="raw output",
            strict=True,
        )


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
    assert "show cts" in commands


def test_package_version_comes_from_project_metadata() -> None:
    assert yenie_parser.__version__ == version("yenie-parser")
