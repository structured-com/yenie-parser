import inspect

import pytest

from yenie_parser.iosxe import _genie_show_fdb as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


FDB_CASES = {
    "ShowMacAddressTable": (
        {},
        "Total Mac Addresses for this criterion: 1\n10 aaaa.bbff.8888 STATIC Gi1/0/8",
        (
            (("total_mac_addresses",), 1),
            (
                (
                    "mac_table",
                    "vlans",
                    "10",
                    "mac_addresses",
                    "aaaa.bbff.8888",
                    "interfaces",
                    "GigabitEthernet1/0/8",
                    "entry_type",
                ),
                "static",
            ),
        ),
    ),
    "ShowMacAddressTableAgingTime": (
        {},
        "Global Aging Time: 300\n10 100",
        ((("mac_aging_time",), 300), (("vlans", "10", "mac_aging_time"), 100)),
    ),
    "ShowMacAddressTableLearning": (
        {},
        "Learning disabled on vlans: 10,101-102",
        ((("vlans", "101", "mac_learning"), False), (("vlans", "102", "vlan"), 102)),
    ),
    "ShowMacAddressMacVlan": (
        {"mac": "0017.0100.0001", "vlan": "10"},
        "10 0017.0100.0001 DYNAMIC Fo1/0/24",
        ((("macAddress", "0017.0100.0001", "Type"), "DYNAMIC"),),
    ),
    "ShowMacAddressTableNotificationChange": (
        {},
        "MAC Notification Feature is Disabled on the switch\n"
        "Interval between Notification Traps : 1 secs\n"
        "Number of MAC Addresses Added : 2\n"
        "Number of MAC Addresses Removed : 3\n"
        "Number of Notifications sent to NMS : 4\n"
        "Maximum Number of entries configured in History Table : 5\n"
        "Current History Table Length : 6\n"
        "MAC Notification Traps are Enabled",
        ((("mac_notification_feature",), "Disabled"), (("mac_notificatn_trps",), "Enabled")),
    ),
    "ShowMacAddressTableNotificationChangeInterface": (
        {"interface": "HundredGigE 2/0/25"},
        "MAC Notification Feature is Disabled on the switch\nHundredGigE2/0/25 Disabled Disabled",
        ((("interface",), "HundredGigE2/0/25"), (("mac_added_trap",), "Disabled")),
    ),
}


@pytest.mark.parametrize("class_name", sorted(FDB_CASES))
def test_fdb_parser_class(class_name: str) -> None:
    kwargs, output, expectations = FDB_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_fdb_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(FDB_CASES)


def test_fdb_empty_output_is_permissive() -> None:
    assert parsers.ShowMacAddressTable().cli(output="") == {}
