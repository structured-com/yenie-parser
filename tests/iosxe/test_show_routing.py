import inspect

import pytest

import yenie_parser
from yenie_parser.iosxe import _genie_show_routing as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


IP_ROUTE_OUTPUT = "C        10.4.1.0/24 is directly connected, GigabitEthernet0/1"

IP_ROUTE_WORD_OUTPUT = """\
Routing entry for 10.4.1.0/24
  Known via "connected", distance 0, metric 0 (connected)
  * directly connected, via GigabitEthernet0/1
"""

IPV6_ROUTE_OUTPUT = """\
IPv6 Routing Table - default - 1 entries
C   2001:DB8:1::/64 [0/0]
     via GigabitEthernet0/0, directly connected
"""

IPV6_ROUTE_WORD_OUTPUT = """\
Routing entry for 2001:DB8:1::/64
  Known via "connected", distance 0, metric 0, type connected
  Route count is 1/1, share count 0
  Routing paths:
    directly connected via GigabitEthernet0/0
"""

IP_CEF_INTERNAL_OUTPUT = """\
10.19.198.239/32, epoch 2, RIB[I], refcnt 7, per-destination sharing
  sources: RIB, RR, LTE
"""

IPV6_CEF_INTERNAL_OUTPUT = """\
2001:DB8::/64, epoch 2, RIB[I], refcnt 7, per-destination sharing
  sources: RIB, RR
"""


ROUTING_CASES = {
    "ShowIpRouteDistributor": (
        {},
        IP_ROUTE_OUTPUT,
        (
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv4",
                    "routes",
                    "10.4.1.0/24",
                    "source_protocol",
                ),
                "connected",
            ),
        ),
    ),
    "ShowIpv6RouteDistributor": (
        {},
        IPV6_ROUTE_OUTPUT,
        (
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv6",
                    "routes",
                    "2001:DB8:1::/64",
                    "route_preference",
                ),
                0,
            ),
        ),
    ),
    "ShowIpv6RouteUpdated": (
        {},
        "IPv6 Routing Table - default - 1 entries\n"
        "LC  2001:1:1:1::1/128 [0/0]\n"
        "  via Loopback0, receive\n"
        "     Last updated 14:15:23 06 December 2017",
        (
            (("ipv6_unicast_routing_enabled",), True),
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv6",
                    "routes",
                    "2001:1:1:1::1/128",
                    "next_hop",
                    "outgoing_interface",
                    "Loopback0",
                    "updated",
                ),
                "14:15:23 06 December 2017",
            ),
        ),
    ),
    "ShowIpCef": (
        {},
        "10.169.197.104/30\n"
        "  nexthop 10.169.197.93 GigabitEthernet0/1 label 22-(local:2043)",
        (
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv4",
                    "prefix",
                    "10.169.197.104/30",
                    "nexthop",
                    "10.169.197.93",
                    "outgoing_interface",
                    "GigabitEthernet0/1",
                    "local_label",
                ),
                2043,
            ),
        ),
    ),
    "ShowIpv6Cef": (
        {},
        "2001:DB8:1:3::/64\n"
        "  nexthop FE80::A8BB:CCFF:FE03:2101 GigabitEthernet0/0 label 18",
        (
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv6",
                    "prefix",
                    "2001:DB8:1:3::/64",
                    "nexthop",
                    "FE80::A8BB:CCFF:FE03:2101",
                    "outgoing_interface",
                    "GigabitEthernet0/0",
                    "outgoing_label",
                ),
                ["18"],
            ),
        ),
    ),
    "ShowIpCefDetail": (
        {"prefix": "10.16.2.2/32"},
        "10.16.2.2/32, epoch 2, per-destination sharing\n"
        "  attached to GigabitEthernet3.100",
        (
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv4",
                    "prefix",
                    "10.16.2.2/32",
                    "per_destination_sharing",
                ),
                True,
            ),
        ),
    ),
    "ShowIpRouteSummary": (
        {},
        "IP routing table name is default (0x0)\n"
        "IP routing table maximum-paths is 32\n"
        "Route Source Networks Subnets Overhead Memory (bytes)\n"
        "connected 2 43 9260 6480\n"
        "Removing Queue Size 0",
        ((("vrf", "default", "route_source", "connected", "memory_bytes"), 6480),),
    ),
    "ShowIpCefInternal": (
        {},
        IP_CEF_INTERNAL_OUTPUT,
        (
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv4",
                    "prefix",
                    "10.19.198.239/32",
                    "refcnt",
                ),
                7,
            ),
        ),
    ),
    "ShowIpv6CefInternal": (
        {},
        IPV6_CEF_INTERNAL_OUTPUT,
        (
            (
                ("vrf", "default", "address_family", "ipv6", "prefix", "2001:DB8::/64", "rib"),
                "[I]",
            ),
        ),
    ),
    "ShowIpv6RouteSummary": (
        {},
        "IPv6 routing table name is default(0) global scope - 526 entries\n"
        "IPv6 routing table default maximum-paths is 16\n"
        "Route Source    Networks    Overhead    Memory (bytes)\n"
        "connected       7           1344        1512\n"
        "/8: 1, /64: 8, /128: 517",
        ((("vrf", "default", "number_of_prefixes", "/128"), 517),),
    ),
    "ShowIpRouteSupernet": (
        {},
        "S        10.0.0.0/8 [1/0] via 192.0.2.1",
        (
            (
                (
                    "vrf",
                    "default",
                    "address_family",
                    "ipv4",
                    "routes",
                    "10.0.0.0/8",
                    "source_protocol",
                ),
                "static",
            ),
        ),
    ),
    "ShowRibClient": (
        {},
        "Client name          Handle     WalkQ  WalkQ by Owner\n"
        "NAT_ROUTE              1          0      0",
        ((("NAT_ROUTE", "handle"), 1),),
    ),
    "ShowBannerMotd": (
        {},
        "*** Authorized Use Only ***\nNo privacy!",
        ((("banner_motd",), "Authorized Use Only  No privacy"),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(ROUTING_CASES))
def test_routing_parser_class(class_name: str) -> None:
    kwargs, output, expectations = ROUTING_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_routing_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(ROUTING_CASES)


def test_route_distributor_uses_word_parser_for_ipv4_route_lookup() -> None:
    parsed = parsers.ShowIpRouteDistributor().cli(
        route="10.4.1.0",
        output=IP_ROUTE_WORD_OUTPUT,
    )

    assert parsed["entry"]["10.4.1.0/24"]["known_via"] == "connected"


def test_route_distributor_uses_word_parser_for_ipv6_route_lookup() -> None:
    parsed = parsers.ShowIpv6RouteDistributor().cli(
        route="2001:DB8:1::/64",
        output=IPV6_ROUTE_WORD_OUTPUT,
    )

    assert parsed["entry"]["2001:DB8:1::/64"]["route_count"] == "1/1"


def test_routing_commands_are_registered() -> None:
    commands = set(yenie_parser.supported_commands("iosxe"))

    assert "show ip route" in commands
    assert "show ipv6 cef internal" in commands
    assert "show ip route vrf {vrf} supernets-only" in commands
    assert "show banner motd" in commands


def test_parse_dispatches_representative_routing_commands() -> None:
    ip_route = yenie_parser.parse(
        platform="iosxe",
        command="show ip route",
        raw_output=IP_ROUTE_OUTPUT,
    )
    ipv6_internal = yenie_parser.parse(
        platform="iosxe",
        command="show ipv6 cef internal",
        raw_output=IPV6_CEF_INTERNAL_OUTPUT,
    )

    assert ip_route["vrf"]["default"]["address_family"]["ipv4"]["routes"]["10.4.1.0/24"][
        "source_protocol"
    ] == "connected"
    assert (
        ipv6_internal["vrf"]["default"]["address_family"]["ipv6"]["prefix"]["2001:DB8::/64"][
            "sharing"
        ]
        == "per-destination"
    )


def test_parse_dispatches_route_word_lookup_despite_overlapping_template() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show ip route 10.4.1.0",
        raw_output=IP_ROUTE_WORD_OUTPUT,
    )

    assert parsed["entry"]["10.4.1.0/24"]["paths"][1]["interface"] == "GigabitEthernet0/1"
