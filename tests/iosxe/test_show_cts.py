import inspect

import pytest

import yenie_parser
from yenie_parser.iosxe import _genie_show_cts as parsers


def _value_at(data: dict, path: tuple[object, ...]) -> object:
    current = data
    for key in path:
        current = current[key]
    return current


SXP_CONNECTIONS_BRIEF_OUTPUT = """\
SXP              : Enabled
Highest Version Supported: 4
Default Password : Set
Default Key-Chain: Not Set
Default Key-Chain Name: Not Applicable
Default Source IP: 192.168.2.24
Connection retry open period: 120 secs
Reconcile period: 120 secs
Retry open timer is not running
Peer-Sequence traverse limit for export: Not Set
Peer-Sequence traverse limit for import: Not Set
Peer_IP Source_IP Conn Status Duration
10.100.123.1 192.168.2.24 On 44:19:54:52 (dd:hr:mm:sec)
Total num of SXP Connections = 1
"""

PACS_OUTPUT = """\
AID: 1100E046659D4275B644BF946EFA49CD
PAC-Info:
PAC-type = Cisco Trustsec
I-ID: gw1
A-ID-Info: Identity Services Engine
Credential Lifetime: 19:56:32 PDT Sun Sep 06 2020
PAC-Opaque: OPAQUE
Refresh timer is set for 6w3d
"""

ROLE_COUNTERS_OUTPUT = """\
Role-based IPv4 counters
From To SW-Denied HW-Denied SW-Permitt HW-Permitt SW-Monitor HW-Monitor
* * 0 0 2 308 0 0
"""

ENVIRONMENT_DATA_OUTPUT = """\
Current state = COMPLETE
Last status = Successful
SGT tag = 0-16:Unknown
State Machine is running
"""

RBACL_OUTPUT = """\
RBACL IP Version Supported: IPv4 & IPv6
name   = PERMIT_IP
IP protocol version = IPV4
refcnt = 2
flag   = 0x41000000
stale  = FALSE
permit tcp dst eq 80
"""

ROLE_PERMISSIONS_OUTPUT = """\
IPv4 Role-based permissions from group 42:Untrusted to group Unknown:
ACCESS-01
Deny IP-00
RBACL Monitor All for Dynamic Policies : FALSE
RBACL Monitor All for Configured Policies : TRUE
"""

INTERFACE_OUTPUT = """\
Global Dot1x feature is Disabled
Interface TenGigabitEthernet1/0/6:
CTS is enabled, mode: MANUAL
IFC state: OPEN
L3 IPM: disabled.
Index : 0 Vlan : 200 SGT : 65200
"""

SXP_CONNECTIONS_OUTPUT = """\
SXP : Enabled
Highest Version Supported: 4
Default Password : Set
Default Key-Chain: Not Set
Default Key-Chain Name: Not Applicable
Default Source IP: 10.1.1.1
Connection retry open period: 120 secs
Reconcile period: 120 secs
Retry open timer is not running
Peer-Sequence traverse limit for export: Not Set
Peer-Sequence traverse limit for import: Not Set
Peer IP : 10.1.1.2
Source IP : 10.1.1.1
Conn status : On
Conn version : 4
Local mode : SXP Speaker
Connection inst# : 1
TCP conn fd : 1
TCP conn password: none
Duration since last state change: 0:00:02:09 (dd:hr:mm:sec)
Total num of SXP Connections = 1
"""

SXP_SGT_MAP_BRIEF_OUTPUT = """\
IPv4,SGT: <10.1.1.8 , 5>
Total number of IP-SGT Mappings: 1
"""

SERVER_LIST_OUTPUT = """\
CTS Server Radius Load Balance = ENABLED
Method = least-outstanding
Batch size = 50
Ignore preferred server
Installed list: SL1, 1 server(s):
*Server: 10.15.20.102, port 1812, A-ID AID1
Status = ALIVE
auto-test = TRUE, keywrap-enable = FALSE, idle-time = 120 mins, deadtime = 20 secs
HTTP Server-list:
Server Name : ise1
Server State : ALIVE
IPv4 Address : 10.0.0.1 (Reachable)
"""

POLICY_SERVER_STATS_OUTPUT = """\
server name : ise1
server state : alive
number of request sent : 8
number of request sent fail : 1
number of response received : 5
number of response recv fail : 3
http 200 ok : 5
http 400 badreq : 0
http 401 unauthorized req : 1
http 403 req forbidden : 0
http 404 notfound : 0
http 408 reqtimeout : 0
http 415 unsupported media : 0
http 500 servererr : 0
http 501 req nosupport : 0
http 503 service unavailable: 0
http 429 too many requests : 0
tcp or tls handshake error : 2
http other error : 0
"""

POLICY_SERVER_DETAILS_OUTPUT = """\
Server Name : ise1
Server Status : Active
IPv4 Address : 10.0.0.1 (Reachable)
Domain-name : ise1.example.com (Reachable)
Trustpoint : TP1
Port-num : 9063
Retransmit count : 3
Timeout : 15
App Content type : JSON
Trustpoint chain : NOT CONFIGURED
IPv6 Address : 1100::101 (Reachable)
"""

POLICY_SGT_OUTPUT = """\
CTS SGT Policy
RBACL Monitor All : FALSE
RBACL IP Version Supported: IPv4 & IPv6
SGT: 30-01:SGT_030
SGT Policy Flag: 0x41400001
Source SGT: 25-00:SGT_025-0, Destination SGT: 30-01:SGT_030-0
rbacl_type = 80
rbacl_index = 1
name   = PERMIT_IP-01
IP protocol version = IPV4
refcnt = 2
flag   = 0x41000000
stale  = FALSE
permit ip log
RBACL Destination List: Not exist
RBACL Multicast List: Not exist
RBACL Policy Lifetime = 86400 secs
RBACL Policy Last update time = 12:55:59 IST Wed Jan 15 2025
Policy expires in 0:22:08:05 (dd:hr:mm:sec)
Policy refreshes in 0:22:08:05 (dd:hr:mm:sec)
Cache data applied = NONE
"""

SXP_SGT_MAP_OUTPUT = """\
SXP Node ID(generated):0xAC171B96(172.23.27.150)
SXP IPv6 Node ID(generated):1133:1:1::2
IPv4,SGT: <100.1.1.123 , 100>
source : SXP;
Peer IP : 33.1.1.1;
Ins Num : 1;
Status : Active;
Seq Num : 9
Peer Seq: AC171BC9
Total number of IP-SGT Mappings: 1
"""


CTS_CASES = {
    "ShowCtsSxpConnectionsBrief": (
        {},
        SXP_CONNECTIONS_BRIEF_OUTPUT,
        ((("sxp_connections", "sxp_peers", "10.100.123.1", "conn_status"), "On"),),
    ),
    "ShowCtsPacs": (
        {},
        PACS_OUTPUT,
        ((("pac_info", "credential_lifetime"), "Sun, Sep/06/2020"),),
    ),
    "ShowCtsRoleBasedCounters": (
        {},
        ROLE_COUNTERS_OUTPUT,
        ((("cts_rb_count", 1, "sw_permit_count"), 2),),
    ),
    "ShowCts": (
        {},
        'CTS device identity: "AAA2220Q2DP"',
        ((("cts_device_identity",), "AAA2220Q2DP"),),
    ),
    "ShowCtsEnvironmentData": (
        {},
        ENVIRONMENT_DATA_OUTPUT,
        ((("cts_env", "state_machine_status"), "running"),),
    ),
    "ShowCtsRbacl": (
        {},
        RBACL_OUTPUT,
        ((("cts_rbacl", "name", "PERMIT_IP", "aces", 1, "port"), 80),),
    ),
    "ShowCtsRoleBasedPermissions": (
        {},
        ROLE_PERMISSIONS_OUTPUT,
        ((("indexes", 1, "src_grp_id"), 42), (("indexes", "monitor_configured"), True)),
    ),
    "ShowCtsWirelessProfilePolicy": (
        {"policy": "xyz-policy"},
        "Policy Profile Name : xyz-policy\n"
        "CTS\n"
        "Role-based enforcement : ENABLED\n"
        "Inline-tagging : DISABLED\n"
        "Default SGT : 100",
        ((("policy_name", "xyz-policy", "default_sgt"), "100"),),
    ),
    "ShowCtsApSgtInfo": (
        {"ap_name": "AP1"},
        "Number of SGTs referred by the AP...............: 1\n"
        "SGT PolicyPushedToAP No.of Clients\n"
        "------------------------------------------------------------\n"
        "UNKNOWN(0) NO 0",
        ((("ap", "AP1", "sgts", "UNKNOWN(0)", "no_of_clients"), 0),),
    ),
    "ShowCtsInterface": (
        {},
        INTERFACE_OUTPUT,
        ((("interfaces", "TenGigabitEthernet1/0/6", "vlan_sgt_map", 0, "sgt"), 65200),),
    ),
    "ShowCtsRolebasedSgtMapIp": (
        {"ip": "1.1.1.1"},
        "IP Address SGT Source\n1.1.1.1 2 SXP",
        ((("1.1.1.1", "source"), "SXP"),),
    ),
    "ShowCtsRoleBasedSgtMapAll": (
        {},
        "Active IPv4-SGT Bindings Information\n"
        "1.1.1.2 2 SXP\n"
        "Total number of SXP bindings = 1",
        ((("ipv4_sgt_bindings", "1.1.1.2", "sgt"), 2),),
    ),
    "ShowCtsSxpConnections": (
        {},
        SXP_CONNECTIONS_OUTPUT,
        ((("10.1.1.2", "conn_version"), 4),),
    ),
    "ShowCtsSxpSgtMapBrief": (
        {},
        SXP_SGT_MAP_BRIEF_OUTPUT,
        ((("ip_sgt_mapping", "ipv4", "10.1.1.8"), 5),),
    ),
    "ShowCtsServerList": (
        {},
        SERVER_LIST_OUTPUT,
        ((("installed_list", "SL1", "10.15.20.102", "keywrap_enable"), False),),
    ),
    "ShowCtsPolicyServerStatistics": (
        {},
        POLICY_SERVER_STATS_OUTPUT,
        ((("cts_policy_server_stats", "ise1", "tcp_or_tls_handshake_err"), 2),),
    ),
    "ShowCtsPolicyServerDetails": (
        {},
        POLICY_SERVER_DETAILS_OUTPUT,
        ((("cts_policy_server_details", "ise1", "ipv6_address", "1100::101"), "Reachable"),),
    ),
    "ShowPlatformSoftwareFedActiveAclSgacl": (
        {"instance": "active"},
        "0 0 0 2610 529",
        ((("active_acl_sgacl_cell", 1, "counter_oid"), 2610),),
    ),
    "ShowCtsInterfaceSummary": (
        {},
        "Twe1/0/12 MANUAL INIT unknown unknown invalid Invalid",
        ((("interface", "Twe1/0/12", "mode"), "MANUAL"),),
    ),
    "ShowCtsPolicySgt": (
        {"sgt": "30"},
        POLICY_SGT_OUTPUT,
        ((("cts_sgt_policy", "rbacl_source_list", 1, "name"), "PERMIT_IP-01"),),
    ),
    "ShowCtsHaSyncStatus": (
        {},
        "CTS environment-data sync to standby is complete or not started.\n"
        "CTS policy sync to standby is complete or not started.",
        ((("cts_ha_sync_status", "policy_sync"), "complete or not started"),),
    ),
    "ShowCtsProvisioningQueue": (
        {},
        "Server: 10.77.128.95, Type: Radius, Provisioned: YES\n"
        "AID: 1695af86d38b22dc7c9500408e2dd35d",
        ((("cts_provisioning_queue", "servers", 1, "provisioned"), "YES"),),
    ),
    "ShowCtsCredentials": (
        {},
        "CTS password is defined in keystore, device-id = cts_admin",
        ((("username",), "cts_admin"),),
    ),
    "ShowCtsSxpSgtMap": (
        {},
        SXP_SGT_MAP_OUTPUT,
        ((("ip_sgt_mappings", 0, "SGT"), 100),),
    ),
    "ShowCtsSxpExportImportGroupDetailed": (
        {"role": "speaker"},
        "Export-import-group: EG1\n"
        "Export-list name: EXP1\n"
        "Import-list name: IMP1\n"
        "vrf blue\n"
        "peer 10.0.0.1",
        ((("peers",), ["10.0.0.1"]),),
    ),
    "ShowCtsKeyStore": (
        {},
        "0 S CTS-password",
        ((("keystore", "0", "name"), "CTS-password"),),
    ),
}


@pytest.mark.parametrize("class_name", sorted(CTS_CASES))
def test_cts_parser_class(class_name: str) -> None:
    kwargs, output, expectations = CTS_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed
    for path, expected in expectations:
        assert _value_at(parsed, path) == expected


def test_all_effective_cts_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(CTS_CASES)


def test_cts_commands_are_registered() -> None:
    commands = set(yenie_parser.supported_commands("iosxe"))

    assert "show cts" in commands
    assert "show cts role-based permissions {ipv4}" in commands
    assert "show cts sxp sgt-map vrf {vrf} brief" in commands
    assert "show platform software fed {switch} {instance} acl sgacl cell all" in commands


def test_parse_dispatches_representative_cts_commands() -> None:
    role_permissions = yenie_parser.parse(
        platform="iosxe",
        command="show cts role-based permissions ipv4",
        raw_output=ROLE_PERMISSIONS_OUTPUT,
    )
    vrf_sgt_map = yenie_parser.parse(
        platform="iosxe",
        command="show cts sxp sgt-map vrf blue brief",
        raw_output=SXP_SGT_MAP_BRIEF_OUTPUT,
    )
    wireless_policy = yenie_parser.parse(
        platform="iosxe",
        command="show cts wireless profile policy xyz-policy",
        raw_output="Policy Profile Name : xyz-policy\n"
        "CTS\n"
        "Role-based enforcement : ENABLED\n"
        "Inline-tagging : DISABLED\n"
        "Default SGT : 100",
    )

    assert role_permissions["indexes"][1]["src_grp_name"] == "Untrusted"
    assert vrf_sgt_map["ip_sgt_mapping"]["total_ip_sgt_mappings"] == 1
    assert wireless_policy["policy_name"]["xyz-policy"]["default_sgt"] == "100"


def test_cts_empty_output_is_permissive() -> None:
    assert parsers.ShowCts().cli(output="") == {}
