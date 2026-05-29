import inspect

import pytest

from yenie_parser.iosxe import _genie_show_interface as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


INTERFACE_CASES = {
    "ShowInterfaces": (
        {},
        "GigabitEthernet1 is up, line protocol is up (connected)\n"
        "  Hardware is Gigabit Ethernet, address is 0057.d2ff.428c "
        "(bia 0057.d2ff.428c)\n"
        "  Internet address is 10.4.4.4/24\n"
        "  MTU 1500 bytes, BW 10000 Kbit/sec, DLY 1000 usec,",
        (
            (("GigabitEthernet1", "connected"), True),
            (("GigabitEthernet1", "bandwidth"), 10000),
        ),
    ),
    "ShowIpInterfaceBrief": (
        {},
        "Interface IP-Address OK? Method Status Protocol\n"
        "GigabitEthernet1 10.0.0.1 YES manual up up",
        ((("interface", "GigabitEthernet1", "ip_address"), "10.0.0.1"),),
    ),
    "ShowIpInterfaceBriefPipeVlan": (
        {},
        "Vlan10 192.0.2.10 YES manual up up",
        ((("interface", "Vlan10", "protocol"), "up"),),
    ),
    "ShowIpInterfaceBriefPipeIp": (
        {"ip": "10.1.18.80"},
        "GigabitEthernet0/0 10.1.18.80 YES manual up up",
        ((("interface", "GigabitEthernet0/0", "interface_status"), "up"),),
    ),
    "ShowInterfacesSwitchport": (
        {},
        "Name: Gi1/0/2\n"
        "Switchport: Enabled\n"
        "Administrative Mode: trunk\n"
        "Operational Mode: trunk",
        ((("GigabitEthernet1/0/2", "switchport_enable"), True),),
    ),
    "ShowIpInterface": (
        {},
        "GigabitEthernet1 is up, line protocol is up\n"
        "Internet address is 10.0.0.1/24\n"
        "MTU is 1500 bytes",
        ((("GigabitEthernet1", "ipv4", "10.0.0.1/24", "prefix_length"), "24"),),
    ),
    "ShowIpv6Interface": (
        {},
        "GigabitEthernet1 is up, line protocol is up\n"
        "IPv6 is enabled, link-local address is FE80::1\n"
        "Global unicast address(es):\n"
        "  2001:DB8::1, subnet is 2001:DB8::/64\n"
        "MTU is 1500 bytes",
        ((("GigabitEthernet1", "ipv6", "2001:DB8::1/64", "prefix_length"), "64"),),
    ),
    "ShowInterfacesTrunk": (
        {},
        "Gi1/0/4 on 802.1q trunking 1\n"
        "Port Vlans allowed on trunk\n"
        "Gi1/0/4 200-211",
        ((("interface", "GigabitEthernet1/0/4", "vlans_allowed_on_trunk"), "200-211"),),
    ),
    "ShowInterfacesCounters": (
        {"interface": "Gi1/0/4"},
        "Port InOctets InUcastPkts InMcastPkts InBcastPkts\nGi1/0/4 10 1 2 3",
        ((("interface", "GigabitEthernet1/0/4", "in", "octets"), 10),),
    ),
    "ShowInterfacesCountersEtherchannel": (
        {"interface": "Po1"},
        "Port InOctets InUcastPkts InMcastPkts InBcastPkts\nPo1 10 1 2 3",
        ((("interface", "Port-channel1", "in", "ucast_pkts"), 1),),
    ),
    "ShowInterfacesAccounting": (
        {},
        "GigabitEthernet0/0/0\nIPV4_UNICAST 9943 797492 50 3568",
        ((("GigabitEthernet0/0/0", "accounting", "ipv4_unicast", "pkts_in"), 9943),),
    ),
    "ShowInterfacesLink": (
        {},
        "Gi1/0/1 Foo 00:00:00 4w5d",
        ((("interfaces", "GigabitEthernet1/0/1", "up_time"), "4w5d"),),
    ),
    "ShowInterfacesStats": (
        {},
        "GigabitEthernet0/0/0\nProcessor 33 2507 33 2490",
        ((("GigabitEthernet0/0/0", "switching_path", "processor", "chars_in"), 2507),),
    ),
    "ShowInterfacesDescription": (
        {},
        "Gi0/1 admin down down to router2",
        ((("interfaces", "GigabitEthernet0/1", "description"), "to router2"),),
    ),
    "ShowInterfacesStatus": (
        {},
        "Gi1/2 Uplink connected 125 full 100 10/100/1000-TX",
        ((("interfaces", "GigabitEthernet1/2", "status"), "connected"),),
    ),
    "ShowInterfacesStatusErrDisabled": (
        {},
        "Fi1/7/0/13 Hello World err-disabled loopdetect",
        ((("interfaces", "FiveGigabitEthernet1/7/0/13", "reason"), "loopdetect"),),
    ),
    "ShowInterfacesTransceiverDetail": (
        {},
        "transceiver is present\n"
        "type is 10Gbase-LR\n"
        "Temperature Threshold Threshold Threshold Threshold\n"
        "Te1/1   25.5 90.0 85.0 -5.0 -10.0",
        ((("interfaces", "TenGigabitEthernet1/1", "Temperature", "Value"), 25.5),),
    ),
    "ShowInterfacesTransceiver": (
        {},
        "Gi1/1 40.6 5.09 0.4 -25.2 -31.00 Max",
        ((("interfaces", "Gi1/1", "max_power"), "Max"),),
    ),
    "ShowMacroAutoInterface": (
        {},
        "Auto Smart Ports Enabled\nFallback : CDP Disabled\nGi2/0/21 TRUE  None CISCO_IPVSC_EVENT",
        ((("interfaces", "GigabitEthernet2/0/21", "macro"), "CISCO_IPVSC_EVENT"),),
    ),
    "ShowInterfaceSummaryVlan": (
        {},
        "Total number of Vlan interfaces: 256\nVlan interfaces configured: 1,10-264",
        ((("Total_vlan_interface",), 256),),
    ),
    "ShowInterfacesSummary": (
        {},
        "* GigabitEthernet1/0/9 0 0 0 0 0 0 0 0 0",
        ((("interfaces", "GigabitEthernet1/0/9", "up"), True),),
    ),
    "ShowInterfacesMtu": (
        {},
        "Fo1/0/1 Interface1 1500",
        ((("interfaces", "FortyGigabitEthernet1/0/1", "mtu"), 1500),),
    ),
    "ShowInterfacesStatusModule": (
        {"mod": "1"},
        "Hu1/0/1 Uplink connected 1 full 40G QSFP 40G AOC5M",
        ((("interfaces", "HundredGigE1/0/1", "port_speed"), "40G"),),
    ),
    "ShowPmVpInterfaceVlan": (
        {"interface": "Gi1/0/1", "vlan": "1001"},
        "vp: 0x50823F64: 3/3(1001) es: 0, stp forwarding, link up, fwd yes",
        ((("pm_vp_info", "vp"), "0x50823F64: 3/3(1001)"),),
    ),
    "ShowInterfacesTransceiverSupportedlist": (
        {},
        "--------- --------\nGLC-FE-100FX-RGD ALL",
        ((("transceiver_type", "GLC-FE-100FX-RGD", "cisco_pin_min_version_supporting_dom"), "ALL"),),
    ),
    "ShowPmPortInterface": (
        {"interface": "Gi1/0/1"},
        "port 1/24 pd 0xA swidb 0xB(switch) sb 0xC",
        ((("pm_port_info", "port"), "1/24"),),
    ),
    "ShowInterfacesPrivateVlanMapping": (
        {},
        "vlan70 71 community",
        ((("secondary_vlan", 71, "interface"), "Vlan70"),),
    ),
    "ShowInterfaceEtherchannel": (
        {"interface_id": "Gi1/0/1"},
        "Port state = Up Mstr In-Bndl\nChannel group = 2 Mode = On Gcchange = -",
        ((("channel_group",), 2),),
    ),
    "ShowInterfacesCapabilities": (
        {},
        "TenGigabitEthernet3/1/3\nModel: WS-C3650-48PD\nType: SFP-10G",
        ((("interface", "TenGigabitEthernet3/1/3", "model"), "WS-C3650-48PD"),),
    ),
    "ShowInterfaceFlowControl": (
        {"interface_id": "Fo2/1/0/10"},
        "Fo2/1/0/10 Unsupp. Unsupp. on on 0 0",
        ((("interface", "port"), "FortyGigabitEthernet2/1/0/10"),),
    ),
    "ShowInterfacesVlanMapping": (
        {"interface": "Gi1/0/1"},
        "20 30 1-to-1",
        ((("vlan_on_wire", "20", "trans_vlan"), 30),),
    ),
    "ShowInterfaceHumanReadableIncludeDrops": (
        {"interface": "Gi1"},
        "Input queue: 0/2000/0/0 (size/max/drops/flushes); Total output drops: 0\n"
        "0 unknown protocol drops",
        ((("unknown_protocol_drops",), 0),),
    ),
    "ShowInterfaceHumanReadable": (
        {"interface": "Gi1"},
        "5 minute input rate 0 bits/sec, 0 packets/sec",
        ((("input",), "0 bits/sec"),),
    ),
    "ShowInterfacesTransceiverProperties": (
        {},
        "Name : Te1/0/1\nAdministrative Speed: 1000\n"
        "Administrative Duplex: full\nMedia Type: SFP",
        ((("interface", "Te1/0/1", "media_type"), "SFP"),),
    ),
    "ShowInterfacesTransceiverModule": (
        {"mod": "1"},
        "Te1/2 50.3 3.25 9.9 -5.7 -4.4",
        ((("interface", "Te1/2", "tx_power"), "-5.7"),),
    ),
    "ShowInterfacePlatform": (
        {"interface": "Gi1/0/45"},
        "GigabitEthernet1/0/45 is up, line protocol is up (connected)\n"
        "Hardware is Gigabit Ethernet, address is 9088.5526.5bad (bia 9088.5526.5bad)\n"
        "MTU 1500 bytes, BW 1000000 Kbit/sec\n"
        "Full-duplex, 1000Mb/s, media type is 10/100/1000BaseTX",
        ((("interfaces", "GigabitEthernet1/0/45", "bandwidth_kbit"), 1000000),),
    ),
    "ShowInterfacesMacAccounting": (
        {},
        "HundredGigE1/0/0\nInput(494 free)\n"
        "0000.0c5d.92f9(58): 1 packets, 106 bytes, last: 4038ms ago\n"
        "Total: 14 packets, 932 bytes",
        ((("HundredGigE1/0/0", "input", "total_packets"), 14),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(INTERFACE_CASES))
def test_interface_parser_class(class_name: str) -> None:
    kwargs, output, expectations = INTERFACE_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_interface_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(INTERFACE_CASES)


def test_interface_empty_output_is_permissive() -> None:
    assert parsers.ShowInterfaces().cli(output="") == {}
