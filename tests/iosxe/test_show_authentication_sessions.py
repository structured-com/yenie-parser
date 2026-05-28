import inspect

import pytest

from yenie_parser.iosxe import _genie_show_authentication_sessions as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


BASIC_DETAIL_OUTPUT = """\
Interface:  GigabitEthernet3/0/2
IIF-ID:  0x1055240000001F6
MAC Address:  0010.00ff.1011
IPv4 Address:  192.0.2.1
Status:  Authorized
Domain:  DATA
Oper host mode:  single-host
Oper control dir:  both
Session timeout:  N/A
Common Session ID:  AC14FC0A0000101200E28D62
Acct Session ID:  Unknown
Handle:  0xDB003227
Current Policy:  dot1x_dvlan_reauth_hm
Method status list:
dot1x Authc Failed
"""

MAC_DETAIL_OUTPUT = """\
Interface:  GigabitEthernet2/0/3
IIF-ID:  0x1D8DDC60
MAC Address:  001a.a136.c68a
IPv6 Address:  Unknown
IPv4 Address:  192.168.194.1
Status:  Authorized
Domain:  VOICE
Oper host mode:  multi-domain
Oper control dir:  both
Session timeout:  50s (server), Remaining: 27s
Common Session ID:  2300130B0000002ABD0A2AF1
Acct Session ID:  0x0000003c
Handle:  0xdb000020
Current Policy:  test_dot1x
Server Policies:
Vlan Group:  Vlan: 194
Method status list:
Method           States
dot1x           Authc Success
"""


AUTH_CASES = {
    "ShowAuthenticationSessions": (
        {},
        "Interface  MAC Address     Method   Domain   Status         Session ID\n"
        "Gi1/48 0015.63ff.a727 dot1x DATA Authz Success 0A3462B1000000102983C05C\n"
        "Session count = 1",
        ((("session_count",), 1), (("interfaces", "GigabitEthernet1/48", "interface"), "GigabitEthernet1/48")),
    ),
    "ShowAuthenticationSessionsInterfaceDetails": (
        {"interface": "Gi1/0/1"},
        BASIC_DETAIL_OUTPUT,
        ((("interfaces", "GigabitEthernet3/0/2", "mac_address", "0010.00ff.1011", "session_timeout", "type"), "N/A"),),
    ),
    "ShowAuthenticationSessionsMACDetails": (
        {"mac_address": "0010.00ff.1011"},
        BASIC_DETAIL_OUTPUT,
        ((("interfaces", "GigabitEthernet3/0/2", "mac_address", "0010.00ff.1011", "domain"), "DATA"),),
    ),
    "AuthenticationDisplayConfigMode": (
        {},
        "Current configuration mode is new-style",
        ((("current_config_mode",), "new-style"),),
    ),
    "ShowAccessSessionsInfo": (
        {},
        "Interface MAC Address M:D:S Vlan IPv4 Policy User-Role\n"
        "Gi3/0/11 0015.0100.0001 D1x:D:AZ UA 200.1.0.1 Dot1x UA\n"
        "Session count = 1",
        ((("interfaces", "GigabitEthernet3/0/11", "client", "0015.0100.0001", "status"), "AZ"),),
    ),
    "ShowSessions": (
        {"switch": "active"},
        "Gi2/0/3 001a.a136.c68a dot1x VOICE Auth 2300130B0000002ABD0A2AF1\nSession count = 1",
        ((("session_count",), 1),),
    ),
    "ShowAuthenticationMacDetails": (
        {"mac": "001a.a136.c68a"},
        MAC_DETAIL_OUTPUT,
        ((("mac", "001a.a136.c68a", "session_timeout", "server"), 50),),
    ),
    "ShowAuthenticationSessionInterface": (
        {"interface": "GigabitEthernet2/0/3", "details": "details"},
        MAC_DETAIL_OUTPUT,
        ((("interfaces", "GigabitEthernet2/0/3", "server_policies", "vlan_group", "vlan"), "194"),),
    ),
    "ShowAuthenticationSessionsSessionId": (
        {"session_id": "2300130B0000002CBD0A520E"},
        "Session id=2300130B0000002CBD0A520E\n"
        "Interface:  GigabitEthernet2/0/3\nIIF-ID:  0x1210405D\n"
        "MAC Address:  0055.6677.8855\nDomain:  DATA\nIPv4 Address:  192.168.10.101\n"
        "Status:  Authorized\nSession timeout:  50s (local), Remaining: 27s\n"
        "Server Policies:\nVlan Group:  Vlan: 10\nMethod status list:\nMethod State\n"
        "dot1x Authc Success",
        ((("session_id", "2300130B0000002CBD0A520E", "session_timeout", "local"), 50),),
    ),
    "ShowAuthenticationSessionInterfaceSwitch": (
        {"interface": "Gi2/0/3"},
        "Gi2/0/3 001a.a136.c68a dot1x VOICE Auth 2300130B0000002ABD0A2AF1\n"
        "Runnable methods list:\n11 5 dot1xSup",
        ((("runnable_methods", 11, "priority"), 5),),
    ),
    "ShowAuthenticationSessionMethod": (
        {"method": "dot1x", "details": "details"},
        MAC_DETAIL_OUTPUT,
        ((("mac", "001a.a136.c68a", "method_status_list", "state"), "Authc Success"),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(AUTH_CASES))
def test_authentication_parser_class(class_name: str) -> None:
    kwargs, output, expectations = AUTH_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_authentication_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(AUTH_CASES)


def test_authentication_empty_output_is_permissive() -> None:
    assert parsers.ShowAuthenticationSessions().cli(output="") == {}
