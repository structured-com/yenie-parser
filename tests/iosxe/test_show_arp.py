import inspect

import pytest

from yenie_parser.iosxe import _genie_show_arp as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


ARP_CASES = {
    "ShowArp": (
        {},
        "Internet 192.168.1.203 3 0015.0100.0001 ARPA Vlan201 pv 203",
        (
            (("interfaces", "Vlan201", "ipv4", "neighbors", "192.168.1.203", "origin"), "dynamic"),
            (
                ("interfaces", "Vlan201", "ipv4", "neighbors", "192.168.1.203", "private_vlan"),
                203,
            ),
        ),
    ),
    "ShowIpArp": (
        {},
        "Internet 10.0.0.1 - aabb.cc00.0100 ARPA Vlan10",
        ((("interfaces", "Vlan10", "ipv4", "neighbors", "10.0.0.1", "origin"), "static"),),
    ),
    "ShowIpArpSummary": (
        {},
        "40 IP ARP entries, with 0 of them incomplete",
        ((("total_entries",), 40), (("incomp_entries",), 0)),
    ),
    "ShowIpTraffic": (
        {},
        "ARP statistics:\n"
        "Rcvd: 2020 requests, 764 replies, 0 reverse, 0 other\n"
        "Sent: 29 requests, 126 replies (2 proxy), 0 reverse\n"
        "Drop due to input queue full: 0",
        (
            (("arp_statistics", "arp_in_requests"), 2020),
            (("arp_statistics", "arp_out_proxy"), 2),
        ),
    ),
    "ShowArpApplication": (
        {},
        "Number of clients registered: 16\nASR1000-RP SPA Ether215 10024",
        (
            (("num_of_clients_registered",), 16),
            (("applications", "ASR1000-RP SPA Ether", "id"), 215),
        ),
    ),
    "ShowArpSummary": (
        {},
        "Total number of entries in the ARP table: 1233.\n"
        "Total number of Dynamic ARP entries: 1123.\n"
        "GigabitEthernet0/0/4 4\n"
        "Learn ARP Entry Threshold is 409600 and Permit Threshold is 486400.\n"
        "Maximum limit of Learn ARP entry : 512000.",
        (
            (("total_num_of_entries", "arp_table_entries"), 1233),
            (("interface_entries", "GigabitEthernet0/0/4"), 4),
            (("maximum_entries", "maximum_limit_of_learn_arp_entry"), 512000),
        ),
    ),
    "ShowIpArpInspectionVlan": (
        {"num": "10"},
        "Source Mac Validation : Disabled\n"
        "Destination Mac Validation : Disabled\n"
        "IP Address Validation : Disabled\n"
        "10 Enabled Active\n"
        "10 Deny Deny Off",
        ((("vlan",), 10), (("operation",), "Active"), (("probe_logging",), "Off")),
    ),
    "ShowAdjacencySummary": (
        {},
        "60004 complete adjacencies\n"
        "0 incomplete adjacencies\n"
        "Database epoch: 0 (60004 entries at this epoch)\n"
        "Summary events epoch is 5\n"
        "Summary events queue contains 0 events (high water mark 389 events)",
        (
            (("adjacencies_summary", "complete_adjacencies"), 60004),
            (("adjacencies_summary", "hwm_events"), 389),
        ),
    ),
    "ShowIpArpInspectionStatisticsVlan": (
        {"num": "10"},
        "10 100 2 3 4\n10 5 6 7 8\n10 9 10 11",
        ((("vlan_id",), 10), (("dhcp_permits",), 5), (("invalid_protocol_data",), 11)),
    ),
    "ShowIpArpInspectionInterfaces": (
        {"interface": "Gi1/0/1"},
        " Gi1/0/1 Untrusted 15 1",
        ((("interfaces", "Gi1/0/1", "state"), "Untrusted"),),
    ),
    "ShowIpArpInspectionLog": (
        {},
        "Total Log Buffer Size : 100\n"
        "Syslog rate : 10 entries per 120 seconds.\n"
        "Gi1/0/37 10 5006.0484.c213 10.1.1.60 1 DHCP Permit "
        "16:35:37 UTC Fri Aug 26 2022",
        (
            (("buffer_size",), 100),
            (("interfaces", "Gi1/0/37", "reason"), "DHCP Permit"),
        ),
    ),
}


@pytest.mark.parametrize("class_name", sorted(ARP_CASES))
def test_arp_parser_class(class_name: str) -> None:
    kwargs, output, expectations = ARP_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_arp_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(ARP_CASES)


def test_arp_empty_output_is_permissive() -> None:
    assert parsers.ShowArp().cli(output="") == {}
