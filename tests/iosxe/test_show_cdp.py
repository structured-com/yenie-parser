import inspect

import pytest

from yenie_parser.iosxe import _genie_show_cdp as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


CDP_CASES = {
    "ShowCdpNeighbors": (
        {},
        "R5.cisco.com Gig 0/0 125 R B Gig 0/0\nTotal cdp entries displayed : 1",
        (
            (("cdp", "index", 1, "device_id"), "R5.cisco.com"),
            (("cdp", "index", 1, "local_interface"), "GigabitEthernet0/0"),
            (("cdp", "index", 1, "port_id"), "GigabitEthernet0/0"),
            (("cdp", "total_entries"), 1),
        ),
    ),
    "ShowCdpNeighborsDetail": (
        {},
        "Device ID: R7\n"
        "Entry address(es):\n"
        "  IP address: 172.16.1.204\n"
        "Platform: cisco C9300-24UX,  Capabilities: Router Switch\n"
        "Interface: GigabitEthernet0/1,  Port ID (outgoing port): GigabitEthernet0/2\n"
        "Holdtime : 126 sec\n"
        "Version :\n"
        "Cisco IOS Software, IOSv Software, Version 15.7(3)M3\n"
        "advertisement version: 2\n"
        "Native VLAN: 42\n"
        "VTP Management Domain: 'Accounting Group'\n"
        "Duplex: full",
        (
            (("total_entries_displayed",), 1),
            (("index", 1, "device_id"), "R7"),
            (("index", 1, "entry_addresses", "172.16.1.204"), {}),
            (("index", 1, "advertisement_ver"), 2),
            (("index", 1, "duplex_mode"), "full"),
        ),
    ),
    "ShowCdpTraffic": (
        {},
        "Total packets output: 297183, Input: 2546\n"
        "Hdr syntax: 0, Chksum error: 1, Encaps failed: 2\n"
        "No memory: 3, Invalid packet: 4,\n"
        "CDP version 1 advertisements output: 5, Input: 6\n"
        "CDP version 2 advertisements output: 7, Input: 8",
        ((("total_output",), 297183), (("checksum",), 1), (("cdp_ver2_input",), 8)),
    ),
    "ShowCdpInterface": (
        {},
        "GigabitEthernet0/1 is up, line protocol is up\n"
        "Encapsulation ARPA\n"
        "Sending CDP packets every 60 seconds\n"
        "Holdtime is 180 seconds\n"
        "cdp enabled interfaces : 1\n"
        "interfaces up          : 1\n"
        "interfaces down        : 0",
        (
            (("interface", "GigabitEthernet0/1", "state"), "up"),
            (("interface", "GigabitEthernet0/1", "cdp_interval"), 60),
            (("interfaces_down",), 0),
        ),
    ),
    "ShowCdpEntry": (
        {},
        "Device ID: 9300-24UX-1\n"
        "Platform: cisco C9300-24UX,  Capabilities: Switch IGMP\n"
        "Interface: GigabitEthernet0/0,  Port ID (outgoing port): GigabitEthernet1/0/18\n"
        "Holdtime : 171 sec\n"
        "Cisco IOS Software, Catalyst L3 Switch Software, Version 15.2(3.1.30)E1\n"
        "advertisement version: 2\n"
        "VTP Management Domain: 'cisco'\n"
        "Native VLAN: 1\n"
        "Duplex: full",
        (
            (
                ("interface", "GigabitEthernet0/0", "port", "GigabitEthernet1/0/18", "device_id"),
                "9300-24UX-1",
            ),
            (
                ("interface", "GigabitEthernet0/0", "port", "GigabitEthernet1/0/18", "native_vlan"),
                1,
            ),
        ),
    ),
    "ShowCdp": (
        {},
        "Sending CDP packets every 60 seconds\n"
        "Sending a holdtime value of 180 seconds\n"
        "Sending CDPv2 advertisements is  enabled",
        ((("interval",), 60), (("holdtime",), 180), (("cdpv2",), "enabled")),
    ),
}


@pytest.mark.parametrize("class_name", sorted(CDP_CASES))
def test_cdp_parser_class(class_name: str) -> None:
    kwargs, output, expectations = CDP_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_cdp_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(CDP_CASES)


def test_cdp_empty_output_is_permissive() -> None:
    assert parsers.ShowCdp().cli(output="") == {}
