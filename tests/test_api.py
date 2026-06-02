import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
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


@pytest.fixture
def isolated_caches() -> Iterator[None]:
    yenie_parser.clear_caches()
    yield
    yenie_parser.clear_caches()


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
        yenie_parser.parse(
            platform="iosxe",
            command="show unsupported command",
            raw_output="",
            strict=True,
        )


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
        command="show unsupported command",
        raw_output="raw output",
        on_failure="empty_dict",
    )

    assert parsed == {}


def test_parse_on_failure_raw_output_returns_original_output() -> None:
    raw_output = "raw output\nwith exact content"

    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show unsupported command",
        raw_output=raw_output,
        on_failure="raw_output",
    )

    assert parsed is raw_output


def test_parse_strict_overrides_on_failure() -> None:
    with pytest.raises(UnsupportedCommandError):
        yenie_parser.parse(
            platform="iosxe",
            command="show unsupported command",
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
            command="show unsupported command",
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
                command="show unsupported command",
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


def test_parse_strict_raises_parser_execution_error(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
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


def test_parse_handles_ambiguous_command(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
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


def test_repeated_parse_calls_reuse_iosxe_registry(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    load_count = 0

    class CountingParser:
        instances = 0

        def __init__(self) -> None:
            type(self).instances += 1

        def cli(self, output: str | None = None) -> dict:
            return {"output": output}

    def load_registry() -> tuple[registry.ParserEntry, ...]:
        nonlocal load_count
        load_count += 1
        return (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached",
                parser_class=CountingParser,
                source_order=1,
            ),
        )

    monkeypatch.setattr(registry, "_load_iosxe_registry", load_registry)

    assert (
        yenie_parser.parse(platform="iosxe", command="show cached", raw_output="first")
        == {"output": "first"}
    )
    assert (
        yenie_parser.parse(platform="iosxe", command="show cached", raw_output="second")
        == {"output": "second"}
    )
    assert load_count == 1
    assert CountingParser.instances == 2


def test_different_commands_reuse_iosxe_registry(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    load_count = 0

    class EchoParser:
        def cli(self, output: str | None = None) -> dict:
            return {"output": output}

    def load_registry() -> tuple[registry.ParserEntry, ...]:
        nonlocal load_count
        load_count += 1
        return (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached one",
                parser_class=EchoParser,
                source_order=1,
            ),
            registry.ParserEntry(
                platform="iosxe",
                template="show cached two",
                parser_class=EchoParser,
                source_order=2,
            ),
        )

    monkeypatch.setattr(registry, "_load_iosxe_registry", load_registry)

    assert (
        yenie_parser.parse(platform="iosxe", command="show cached one", raw_output="one")
        == {"output": "one"}
    )
    assert (
        yenie_parser.parse(platform="iosxe", command="show cached two", raw_output="two")
        == {"output": "two"}
    )
    assert load_count == 1


def test_clear_caches_reloads_iosxe_registry(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    load_count = 0

    class EchoParser:
        def cli(self, output: str | None = None) -> dict:
            return {"output": output}

    def load_registry() -> tuple[registry.ParserEntry, ...]:
        nonlocal load_count
        load_count += 1
        return (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached",
                parser_class=EchoParser,
                source_order=load_count,
            ),
        )

    monkeypatch.setattr(registry, "_load_iosxe_registry", load_registry)

    first_registry = registry.get_registry("iosxe")
    assert registry.get_registry(" IOSXE ") is first_registry
    assert load_count == 1

    yenie_parser.clear_caches()

    second_registry = registry.get_registry("iosxe")
    assert second_registry is not first_registry
    assert load_count == 2


def test_find_matches_cache_returns_fresh_kwargs(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    class EchoParser:
        def cli(self, value: str, output: str | None = None) -> dict:
            return {"value": value, "output": output}

    monkeypatch.setattr(
        registry,
        "_load_iosxe_registry",
        lambda: (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached {value}",
                parser_class=EchoParser,
                source_order=1,
            ),
        ),
    )

    first_matches = registry.find_matches("iosxe", "show cached thing")
    first_matches[0].kwargs["value"] = "mutated"

    second_matches = registry.find_matches("iosxe", "show cached thing")

    assert second_matches[0].kwargs == {"value": "thing"}


def test_threaded_cold_start_reuses_single_registry_load(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    load_count = 0

    class EchoParser:
        def cli(self, output: str | None = None) -> dict:
            return {"output": output}

    def load_registry() -> tuple[registry.ParserEntry, ...]:
        nonlocal load_count
        load_count += 1
        time.sleep(0.02)
        return (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached",
                parser_class=EchoParser,
                source_order=1,
            ),
        )

    monkeypatch.setattr(registry, "_load_iosxe_registry", load_registry)

    def parse_cached(_: int) -> dict | str | None:
        return yenie_parser.parse(platform="iosxe", command="show cached", raw_output="raw")

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(parse_cached, range(16)))

    assert results == [{"output": "raw"}] * 16
    assert load_count == 1


def test_preload_warms_registry_without_parser_instantiation(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    load_count = 0

    class CountingParser:
        instances = 0

        def __init__(self) -> None:
            type(self).instances += 1

        def cli(self, output: str | None = None) -> dict:
            return {"output": output}

    def load_registry() -> tuple[registry.ParserEntry, ...]:
        nonlocal load_count
        load_count += 1
        return (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached",
                parser_class=CountingParser,
                source_order=1,
            ),
        )

    monkeypatch.setattr(registry, "_load_iosxe_registry", load_registry)

    yenie_parser.preload()

    assert load_count == 1
    assert CountingParser.instances == 0

    assert (
        yenie_parser.parse(platform="iosxe", command="show cached", raw_output="raw")
        == {"output": "raw"}
    )
    assert load_count == 1
    assert CountingParser.instances == 1


def test_preload_with_commands_warms_exact_command_matches(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    class CountingParser:
        instances = 0

        def __init__(self) -> None:
            type(self).instances += 1

        def cli(self, value: str, output: str | None = None) -> dict:
            return {"value": value, "output": output}

    monkeypatch.setattr(
        registry,
        "_load_iosxe_registry",
        lambda: (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached {value}",
                parser_class=CountingParser,
                source_order=1,
            ),
        ),
    )

    yenie_parser.preload(platform=" IOSXE ", commands=["show cached thing"])

    assert ("iosxe", "show cached thing") in registry._FIND_MATCHES_CACHE
    assert CountingParser.instances == 0

    assert (
        yenie_parser.parse(platform="iosxe", command="show cached thing", raw_output="raw")
        == {"value": "thing", "output": "raw"}
    )
    assert CountingParser.instances == 1


def test_preload_none_warms_all_template_matches_with_bounded_cache(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    class EchoParser:
        def cli(self, output: str | None = None) -> dict:
            return {"output": output}

    monkeypatch.setattr(
        registry,
        "_load_iosxe_registry",
        lambda: (
            registry.ParserEntry(
                platform="iosxe",
                template="show cached one",
                parser_class=EchoParser,
                source_order=1,
            ),
            registry.ParserEntry(
                platform="iosxe",
                template="show cached two",
                parser_class=EchoParser,
                source_order=2,
            ),
            registry.ParserEntry(
                platform="iosxe",
                template="show cached three",
                parser_class=EchoParser,
                source_order=3,
            ),
        ),
    )
    monkeypatch.setattr(registry, "_FIND_MATCHES_CACHE_MAXSIZE", 2)

    yenie_parser.preload(commands=None)

    assert len(registry._FIND_MATCHES_CACHE) == 2
    assert ("iosxe", "show cached two") in registry._FIND_MATCHES_CACHE
    assert ("iosxe", "show cached three") in registry._FIND_MATCHES_CACHE


def test_preload_empty_commands_warms_entry_metadata_without_match_cache(
    monkeypatch: pytest.MonkeyPatch, isolated_caches: None
) -> None:
    class EchoParser:
        def cli(self, output: str | None = None) -> dict:
            return {"output": output}

    entry = registry.ParserEntry(
        platform="iosxe",
        template="show cached {value}",
        parser_class=EchoParser,
        source_order=1,
    )
    monkeypatch.setattr(registry, "_load_iosxe_registry", lambda: (entry,))

    yenie_parser.preload(commands=[])

    assert registry._FIND_MATCHES_CACHE == {}
    assert entry.__dict__["normalized_template"] == "show cached {value}"
    assert entry.__dict__["placeholder_names"] == ("value",)
    assert entry.__dict__["literal_count"] == 2
    assert entry.__dict__["_tokens"] == ("show", "cached", "{value}")
    assert "_pattern" in entry.__dict__


def test_preload_raises_for_unsupported_platform(isolated_caches: None) -> None:
    with pytest.raises(UnsupportedPlatformError):
        yenie_parser.preload(platform="nxos")


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
