import inspect

import pytest

from yenie_parser.iosxe import _genie_show_device_tracking as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


DEVICE_CASES = {
    "ShowDeviceTrackingDatabase": (
        {},
        "Binding Table has 1 entries, 0 dynamic (limit 200000)\n"
        "L 10.22.66.10 7081.05ff.eb40 Vl230 230 0100 10194mn REACHABLE",
        ((("binding_table_count",), 1), (("device", 1, "pref_level_code"), 100)),
    ),
    "ShowDeviceTrackingDatabaseInterface": (
        {"interface": "Gi1/0/1"},
        "Binding Table has 1 entries, 1 dynamic (limit 100000)\n"
        "DH4 10.160.43.197 94d4.69ff.e606 Te8/0/37 1023 0025 116s REACHABLE 191 s",
        ((("binding_table", "limit"), 100000), (("network_layer_address", "10.160.43.197", "vlan"), 1023)),
    ),
    "ShowDeviceTrackingPolicies": (
        {},
        "Target Type Policy Feature Target range\nvlan 39 VLAN test1 Device-tracking vlan all",
        ((("policies", 1, "target"), "vlan 39"),),
    ),
    "ShowDeviceTrackingPolicy": (
        {"policy_name": "test"},
        "Device-tracking policy test configuration:\n"
        "trusted-port\nsecurity-level guard\ndevice-role node\n"
        "gleaning from Neighbor Discovery protecting prefix-list foo\n"
        "limit address-count for IPv4 per mac 5\n"
        "Target Type Policy Feature Target range\n"
        "Twe1/0/42 PORT test Device-tracking vlan all",
        ((("configuration", "limit_address_count", "ipv4"), 5),),
    ),
    "ShowIpv6RaGuardPolicy": (
        {"policy_name": "asdf"},
        "RA guard policy asdf configuration:\ndevice-role router\ntrusted-port\n"
        "hop-limit minimum 1\nTarget Type Policy Feature Target range\n"
        "Twe1/0/42 PORT asdf RA guard vlan all",
        ((("configuration", "min_hop_limit"), 1),),
    ),
    "ShowIpv6SourceGuardPolicy": (
        {"policy_name": "test1"},
        "Source guard policy test1 configuration:\ntrusted\nvalidate address\n"
        "Target Type Policy Feature Target range\nTwe1/0/42 PORT test1 Source guard vlan all",
        ((("configuration", "validate_address"), "yes"),),
    ),
    "ShowDeviceTrackingCountersVlan": (
        {"vlanid": "39"},
        "Received messages on vlan 39   :\nNDP RS[1] NS[2]",
        ((("vlanid", 39, "received", "ndp", "RS"), 1),),
    ),
    "ShowDeviceTrackingDatabaseMac": (
        {},
        "dead.beef.0001 Twe1/0/42 39 NO TRUST MAC-STALE N/A test1 49",
        ((("device", 1, "input_index"), 49),),
    ),
    "ShowDeviceTrackingDatabaseMacMac": (
        {"mac": "dead.beef.0001"},
        "macDB has 1 entries for mac dead.beef.0001,vlan 38, 0 dynamic\n"
        "S 10.10.10.11 dead.beef.0001 Twe1/0/41 38 0100 4s REACHABLE 308 s",
        (((38, "entries", 1, "pref_level_code"), 100),),
    ),
    "ShowDeviceTrackingDatabaseMacMacDetails": (
        {"mac": "dead.beef.0001"},
        "Binding table configuration:\nmax/box : no limit\nBinding table current counters:\n"
        "dynamic : 0\nBinding table counters by state:\nREACHABLE : 1\n"
        "macDB has 1 entries for mac dead.beef.0001,vlan 38, 0 dynamic\n"
        "S 10.10.10.11 dead.beef.0001(R) Twe1/0/41 trunk 38 ( 38) 0100 63s "
        "REACHABLE 249 s no yes 0000.0000.0000",
        ((("entries", 1, "pref_level_code"), 100),),
    ),
    "ShowDeviceTrackingCountersInterface": (
        {"interface": "Gi1/0/1"},
        "Received messages on Gi1/0/1:\nNDP RS[1] NS[2]",
        ((("interface", "GigabitEthernet1/0/1", "message_type", "received", "protocols", "ndp", "rs"), 1),),
    ),
    "ShowDeviceTrackingEvents": (
        {},
        "[Fri Jun 18 22:14:40.000] SSID 0 FSM Feature Table running for event "
        "ACTIVE_REGISTER in state CREATING",
        ((("ssid", 0, "events", 1, "event_type"), "fsm_run"),),
    ),
    "ShowDeviceTrackingFeatures": (
        {},
        "Device-tracking   128   READY",
        ((("features", "Device-tracking", "priority"), 128),),
    ),
    "ShowDeviceTrackingDatabaseMacDetails": (
        {},
        "S dead.beef.0001 Twe1/0/41 38 TRUSTED MAC-STALE 93013 s test1 60\n"
        "Attached IP: 10.10.10.11",
        ((("device", 1, "attached", 1, "ip"), "10.10.10.11"),),
    ),
    "ShowDeviceTrackingMessages": (
        {},
        "[Wed Jul 21 20:31:23.000] VLAN 1, From Et0/1 MAC aabb.cc00.0300: "
        "ARP::REP, 192.168.23.3,",
        ((("entries", 1, "interface"), "Ethernet0/1"),),
    ),
    "ShowDeviceTrackingDatabaseInterfaceCount": (
        {"interface": "Gi1/0/1", "match": "foo"},
        "Number of lines which match regexp = 240",
        ((("count",), 240),),
    ),
    "ShowDeviceTrackingCapturePolicy": (
        {},
        "HW Policy 0000039C #targets:2\nTarget Gi1/0/4 type 0 handle 40B\n"
        "HW Target Gi1/0/4 HW policy signature 0000039C policies#:2 rules#:6 sig 0000039C\n"
        "SW policy dhcp_client feature DHCP Guard\n"
        "Rule DHCP SERVER SOURCE Protocol UDP mask 00000200 action PUNT match1 0 match2 546 #feat:1",
        ((("target_db", "Gi1/0/4", "rules"), 6),),
    ),
    "ShowDeviceTrackingDatabaseDetails": (
        {},
        "Binding table configuration:\nmax/box : no limit\nBinding table current counters:\n"
        "dynamic : 1\nBinding table counters by state:\nREACHABLE : 1\n"
        "vlanDB has 10 entries for vlan 39, 5 dynamic\n"
        "portDB has 15 entries for interface Twe1/0/42, 8 dynamic\n"
        "Network Layer Address Link Layer Address Interface mode vlan(prim) prlvl age state "
        "Time left Filter In Crimson Client ID Policy (feature)\n"
        "S 10.10.10.10 dead.beef.0001(S) Twe1/0/42 access 39 ( 39) 0100 59mn "
        "STALE N/A no yes 0000.0000.0000",
        ((("vlandb", "dynamic_entries"), 5), (("device", 1, "pref_level_code"), 100)),
    ),
    "ShowDeviceTrackingMessagesDetailedNum": (
        {"number": "1"},
        "[Mon Sep 02 05:45:03.000] VLAN 50, From Gi3/0/46 seclvl [glean], "
        "MAC b07d.479e.7d9a: DHCPv6::REN,\n"
        "1 addresses advertised:\nIPv6 addr: FE80::7ABC:1AFF:FEC2:EEE5",
        ((("messages", 0, "num_addresses"), 1),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(DEVICE_CASES))
def test_device_tracking_parser_class(class_name: str) -> None:
    kwargs, output, expectations = DEVICE_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_device_tracking_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(DEVICE_CASES)


def test_device_tracking_empty_output_is_permissive() -> None:
    assert parsers.ShowDeviceTrackingDatabase().cli(output="") == {}
