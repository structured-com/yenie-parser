import inspect

import pytest

import yenie_parser
from yenie_parser.iosxe import _genie_show_run as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


RUN_CASES = {
    "ShowRunPolicyMap": (
        {"name": "PM1"},
        "policy-map PM1\n"
        " class CLASS1\n"
        "  police cir 400000 conform-action transmit exceed-action drop\n"
        "  set dscp ef\n"
        "  bandwidth percent 25",
        (
            (("policy_map", "PM1", "class", "CLASS1", "police", "cir_bps"), "400000"),
            (("policy_map", "PM1", "class", "CLASS1", "qos_set", "dscp"), "ef"),
        ),
    ),
    "ShowRunInterface": (
        {"interface": "GigabitEthernet1"},
        "interface GigabitEthernet1\n"
        " description Uplink\n"
        " ip address 10.0.0.1 255.255.255.0\n"
        " shutdown",
        ((("interfaces", "GigabitEthernet1", "ipv4", "ip"), "10.0.0.1"),),
    ),
    "ShowRunInterfaceAllSectionInterface": (
        {},
        "interface GigabitEthernet2\n"
        " description Downlink\n"
        " ip address 10.0.1.1 255.255.255.0",
        ((("interfaces", "GigabitEthernet2", "description"), "Downlink"),),
    ),
    "ShowRunMdnsSd": (
        {},
        "mdns-sd gateway\nmode service-peer\nactive-query timer 10",
        ((("mdns_gateway", "mode"), "service-peer"),),
    ),
    "ShowRunAllSectionInterface": (
        {"interface": "GigabitEthernet1"},
        "interface GigabitEthernet1\n"
        " description Access\n"
        " switchport access vlan 10\n"
        " spanning-tree portfast",
        ((("interfaces", "GigabitEthernet1", "switchport_access_vlan"), "10"),),
    ),
    "ShowRunningAAAUserName": (
        {},
        "user-name testuser\ncreation-time 1628765288\nprivilege 15\npassword 0 lab",
        ((("username", "testuser", "password", "password"), "lab"),),
    ),
    "ShowRunningConfigAAAUsername": (
        {},
        "username developer privilege 15 secret 9 SECRET",
        ((("username", "developer", "privilege"), 15),),
    ),
    "ShowRunningConfigFlowMonitor": (
        {},
        "flow monitor monitor_l2_in\n"
        " exporter Exporter1\n"
        " cache timeout active 60\n"
        " record record_l2_in",
        ((("flow_monitor_name", "monitor_l2_in", "cache_timeout_time"), 60),),
    ),
    "ShowRunningConfigAAA": (
        {},
        "aaa new-model\n"
        "radius server RADIUS_1\n"
        " address ipv4 11.15.24.213 auth-port 1812 acct-port 1813\n"
        " key Cisco123\n"
        "aaa group server radius RADIUS_GROUP\n"
        " server name RADIUS_1\n"
        " ip vrf forwarding newVRF2\n"
        " ip radius source-interface TenGigabitEthernet1/0/13\n"
        "aaa session-id common",
        ((("radius", "server", "RADIUS_1", "auth_port"), 1812),),
    ),
    "ShowRunningConfigNve": (
        {},
        "l2vpn evpn\n"
        " replication-type ingress\n"
        " router-id loopback 0\n"
        " default-gateway advertise\n"
        "vlan configuration 200\n"
        " member vni 5000\n"
        "interface nve1\n"
        " no ip address\n"
        " host-reachability protocol bgp\n"
        " source-interface loopback1\n"
        " member vni 6000 ingress-replication",
        ((("nve_interfaces", "1", "vni", "l2vni", "6000", "replication_type"), "ingress-replication"),),
    ),
    "ShowRunRoute": (
        {},
        "ip route 10.64.67.187 255.255.255.255 9.30.0.1",
        ((("routes", 0), "ip route 10.64.67.187 255.255.255.255 9.30.0.1"),),
    ),
    "ShowRunSectionBgp": (
        {},
        "router bgp 65000\n"
        " bgp router-id 172.16.255.4\n"
        " neighbor 10.11.11.11 remote-as 1\n"
        " address-family ipv4\n"
        " redistribute connected",
        ((("bgp", 65000, "address_family", "ipv4", "redistribute_connected"), True),),
    ),
    "ShowRunSectionVrfDefinition": (
        {},
        "vrf definition ce1\nrd 2:2\naddress-family ipv4\nroute-target import 3:201",
        ((("vrf", "ce1", "address_family", "ipv4", "route_target", 0, "rt"), "3:201"),),
    ),
    "ShowRunSectionMacAddress": (
        {},
        "mac address-table static 0075.c3e4.b824 vlan 1000 drop",
        ((("mac_address",), "0075.c3e4.b824"),),
    ),
    "ShowRunningConfigAllClassMap": (
        {"class_map": "system-cpp-default-v4"},
        "class system-cpp-default-v4\npolice rate 2000 pps",
        ((("class", "system-cpp-default-v4", "police", "rate_pps"), 2000),),
    ),
    "ShowRunningConfigAAARadiusServer": (
        {},
        "radius server TMP_NAME\n"
        " address ipv4 16.0.0.104\n"
        " key radius/dtls\n"
        " dtls port 2083\n"
        " dtls watchdoginterval 2\n"
        " dtls retries 2\n"
        " dtls trustpoint client Client\n"
        " dtls trustpoint server Server",
        ((("radius_server", "TMP_NAME", "dtls_port"), 2083),),
    ),
    "ShowRunningConfigVrf": (
        {},
        "ip vrf CUST_A\n"
        " rd 100:1\n"
        " route-target export 100:1\n"
        "interface TenGigabitEthernet0/0/8\n"
        " ip vrf forwarding CUST_A\n"
        " ip address 15.0.0.1 255.255.255.0\n"
        "ip route vrf CUST_A 15.0.0.0 255.0.0.0 TenGigabitEthernet0/0/8 15.0.0.2",
        ((("vrf", "CUST_A", "routes", "route_1", "next_hop"), "15.0.0.2"),),
    ),
    "ShowRunSectionAlarm": (
        {},
        "alarm-profile defaultPort\n"
        " alarm not-operating\n"
        "alarm facility temperature primary low 0\n"
        "alarm facility hsr enable\n"
        "no logging alarm\n"
        "snmp mib flowmon alarmhistorysize 500",
        ((("alarm_facility", "temperature primary", "thresholds", "low"), 0),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(RUN_CASES))
def test_show_run_parser_class(class_name: str) -> None:
    kwargs, output, expectations = RUN_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_show_run_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(RUN_CASES)


def test_show_run_commands_are_registered() -> None:
    commands = set(yenie_parser.supported_commands("iosxe"))

    assert "show run policy-map {name}" in commands
    assert "show running-config interface {interface}" in commands
    assert "show running-config | section bgp" in commands
    assert "show running-config vrf" in commands


def test_parse_dispatches_show_run_policy_map() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show run policy-map PM1",
        raw_output=RUN_CASES["ShowRunPolicyMap"][1],
    )

    assert parsed["policy_map"]["PM1"]["class"]["CLASS1"]["qos_set"]["dscp"] == "ef"
