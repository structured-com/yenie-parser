import inspect

import pytest

import yenie_parser
from yenie_parser.iosxe import _genie_show_aaa as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


AAA_SERVERS_OUTPUT = """\
RADIUS: id 9, priority 1, host 11.15.24.174, auth-port 1812, acct-port 1813, hostname ISE-RAD
State: current UP, duration 294173s, previous duration 0s
Quarantined: No
"""

AAA_DEAD_CRITERIA_OUTPUT = """\
Address   : 11.19.12.66
Auth Port : 1645
Acct Port : 1646
Server Group  : radius
Configured Retransmits   : 3
Configured Timeout       : 5
Max Computed Outstanding Transactions: 2
Max Computed Retransmits : 20
"""


AAA_CASES = {
    "ShowAAServers": (
        {},
        AAA_SERVERS_OUTPUT,
        ((("radius_server", "11.15.24.174", "hostname"), "ISE-RAD"),),
    ),
    "ShowAAAUserAll": (
        {},
        "Unique id 13 is currently in use.\n"
        "NET: Username=(n/a)\n"
        "Session Id=0000137E Unique Id=00001388\n"
        "Authen: service=LOGIN type=ASCII method=NONE",
        ((("unique_id", "id_13", "authen", "method"), "NONE"),),
    ),
    "ShowAaaFqdnAll": (
        {},
        "FQDN Name : fqdnname\n"
        "Protocol  : RADIUS\n"
        "IPv4s     : 11.15.24.213\n"
        "Groups    : FQDNNAME radius",
        ((("fqdn_name", "fqdnname", "ipv4s"), "11.15.24.213"),),
    ),
    "ShowAAACacheGroup": (
        {"server_grp": "grp"},
        "MAC ADDR:      000A.0A00.0500\n"
        "Profile Name: regProfile\n"
        "User Name:          test\n"
        "Timeout:            86400\n"
        "Total number of Cache entries is 1",
        ((("client", "000A.0A00.0500", "timeout"), 86400),),
    ),
    "ShowAAACommonCriteraPolicy": (
        {"policy_name": "enable_1"},
        "Policy name: enable_1\n"
        "Minimum length: 10\n"
        "Upper Count: 1\n"
        "Number of character changes 4\n"
        "Valid for 10 days 2 hours",
        ((("lifetime", "days"), 10),),
    ),
    "ShowAAAMethodList": (
        {"type": "authen"},
        "authen queue=AAA_ML_AUTHEN_LOGIN\n"
        "name= pvt_authen_0 valid=TRUE id=97000002 :state=DEAD : SERVER_GROUP  private_sg-0",
        ((("authen", "queue", "AAA_ML_AUTHEN_LOGIN", "valid"), True),),
    ),
    "ShowAaaDeadCriteriaRadius": (
        {"server_name": "R1"},
        AAA_DEAD_CRITERIA_OUTPUT,
        ((("statistics", "max_computed_retransmit"), 20),),
    ),
    "ShowAaaSessions": (
        {},
        "Total sessions since last reload: 6\n"
        "Session Id: 4003\n"
        "  Unique Id: 13\n"
        "  User Name: *not available*\n"
        "  IP Address: 0.0.0.0\n"
        "  Idle Time: 0\n"
        "  CT Call Handle: 0",
        ((("aaa_sessions", "4003", "ct_call_handle"), 0),),
    ),
    "ShowAaaMemory": (
        {},
        "AAA Acct Rec ch           :        252/10248      (  2%) [      3] Chunk\n"
        "Total allocated: 0.398 Mb, 408 Kb, 418356 bytes\n"
        "Authentication low-memory threshold      : 3%\n"
        "PoD  Packet dropped                      : 0",
        ((("low_memory", "pod_pkt_drop"), 0),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(AAA_CASES))
def test_aaa_parser_class(class_name: str) -> None:
    kwargs, output, expectations = AAA_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_aaa_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(AAA_CASES)


def test_aaa_commands_are_registered() -> None:
    commands = set(yenie_parser.supported_commands("iosxe"))

    assert "show aaa servers" in commands
    assert "show aaa cache group {server_grp} profile {profile}" in commands
    assert "show aaa dead-criteria radius server-name {server_name}" in commands
    assert "show aaa memory" in commands


def test_parse_dispatches_representative_aaa_commands() -> None:
    servers = yenie_parser.parse(
        platform="iosxe",
        command="show aaa servers",
        raw_output=AAA_SERVERS_OUTPUT,
    )
    dead_criteria = yenie_parser.parse(
        platform="iosxe",
        command="show aaa dead-criteria radius server-name R1",
        raw_output=AAA_DEAD_CRITERIA_OUTPUT,
    )

    assert servers["radius_server"]["11.15.24.174"]["priority"] == 1
    assert dead_criteria["server"]["auth_port"] == 1645


def test_aaa_empty_output_is_permissive() -> None:
    assert parsers.ShowAaaSessions().cli(output="") == {}
