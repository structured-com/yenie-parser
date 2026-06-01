# ruff: noqa
import inspect

import pytest

import yenie_parser

from yenie_parser.iosxe import _genie_show_platform as parsers

ENV_OUTPUT = "Switch 1 FAN 1 is OK"
CPU_PLATFORM_OUTPUT = "CPU utilization for five seconds: 43%, one minute: 44%, five minutes: 44%"
CPU_SORTED_OUTPUT = "CPU utilization for five seconds: 5%/1%; one minute: 6%; five minutes: 6%"
MEMORY_OUTPUT = "Processor Pool Total: 10147887840 Used: 485435960 Free: 9662451880"
NAT_TRANSLATION_OUTPUT = "TCP 135.0.0.2:0 192.0.0.2:0 193.0.0.2:0 193.0.0.2:0"
NAT_STATS_OUTPUT = "NAT Type : Static\nNetflow Type : NA\nFlow Record  : Disabled\nDynamic NAT entries  : 0 entries\nStatic NAT entries : 0 entries\nTotal NAT entries : 0 entries\nTotal HW Resource (TCAM): 26 of 27648 /0 .09% utilization"
SYSTEM_STATS_OUTPUT = "Syspage index for the Fastpath thread: 6"
SHOW_VERSION_C9300_OUTPUT = """Cisco IOS XE Software, Version 17.03.04
Cisco IOS Software [Amsterdam], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.3.4, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2021 by Cisco Systems, Inc.
Compiled Sat 03-Jul-21 01:55 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2021 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMON
BOOTLDR: System Bootstrap, Version 17.3.2r, RELEASE SOFTWARE (P)

chi-csw-01 uptime is 4 years, 5 weeks, 6 days, 3 hours, 55 minutes
Uptime for this control processor is 4 years, 5 weeks, 6 days, 3 hours, 56 minutes
System returned to ROM by Image Install
System restarted at 14:51:16 UTC Fri Apr 22 2022
System image file is "flash:packages.conf"
Last reload reason: Image Install



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.


Technology Package License Information:

------------------------------------------------------------------------------
Technology-package                                     Technology-package
Current                        Type                       Next reboot
------------------------------------------------------------------------------
network-advantage   \tSmart License                 \t network-advantage
dna-advantage       \tSubscription Smart License    \t dna-advantage
AIR License Level: AIR DNA Advantage
Next reload AIR license Level: AIR DNA Advantage


Smart Licensing Status: Registration Not Applicable/Not Applicable

cisco C9300-24T (X86) processor with 1331366K/6147K bytes of memory.
Processor board ID FJC2402T0HV
20 Virtual Ethernet interfaces
28 Gigabit Ethernet interfaces
8 Ten Gigabit Ethernet interfaces
2 TwentyFive Gigabit Ethernet interfaces
2 Forty Gigabit Ethernet interfaces
2048K bytes of non-volatile configuration memory.
8388608K bytes of physical memory.
1638400K bytes of Crash Files at crashinfo:.
11264000K bytes of Flash at flash:.
117219783K bytes of USB Flash at usbflash1:.

Base Ethernet MAC Address          : 4c:e1:76:25:67:00
Motherboard Assembly Number        : 73-18270-03
Motherboard Serial Number          : FJZ24010EPA
Model Revision Number              : A0
Motherboard Revision Number        : B0
Model Number                       : C9300-24T
System Serial Number               : FJC2402T0HV
CLEI Code Number                   :


Switch Ports Model              SW Version        SW Image              Mode
------ ----- -----              ----------        ----------            ----
*    1 41    C9300-24T          17.03.04          CAT9K_IOSXE           INSTALL


Configuration register is 0x102
"""

SHOW_PLATFORM_CASES = {
    "ShowBootvar": ({}, "BOOT variable = flash:image.bin;\nConfiguration register is 0x2102"),
    "ShowVersion": ({}, "Cisco IOS Software [Fuji], ASR1000 Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.7.1prd4, RELEASE SOFTWARE (fc1)\nRouter uptime is 1 day"),
    "Dir": ({"directory": "flash:/"}, "Directory of flash:/\n1 -rw- 123 Jan 1 2026 00:00:00 +00:00 file.txt\n123456 bytes total (123 bytes free)"),
    "ShowRedundancy": ({}, "Available System Uptime = 1 day"),
    "ShowRedundancyStates": ({}, "my state = 13 -ACTIVE"),
    "ShowInventory": ({}, 'NAME: "Chassis", DESCR: "Cisco ASR1006 Chassis"\nPID: ASR1006 , VID: V01 , SN: SN1'),
    "ShowPlatform": ({}, "Chassis type: ASR1006"),
    "ShowBoot": ({}, "BOOT variable = flash:image.bin;"),
    "ShowSwitchDetail": ({}, "Switch/Stack Mac Address : 0057.d2ff.e71b - Local Mac Address"),
    "ShowSwitch": ({}, "Switch/Stack Mac Address : 0057.d2ff.e71b - Local Mac Address"),
    "ShowEnvironmentAll": ({}, ENV_OUTPUT),
    "ShowEnvAll": ({}, ENV_OUTPUT),
    "ShowEnvFan": ({}, ENV_OUTPUT),
    "ShowEnvPower": ({}, ENV_OUTPUT),
    "ShowEnvPowerAll": ({}, ENV_OUTPUT),
    "ShowEnvRPS": ({}, ENV_OUTPUT),
    "ShowEnvStack": ({}, ENV_OUTPUT),
    "ShowEnvTemperature": ({}, ENV_OUTPUT),
    "ShowEnvTemperatureStatus": ({}, ENV_OUTPUT),
    "ShowModule": ({}, "1 56 WS-C3850-48P-E FOC1902X062 689c.e2ff.b9d9 V04 16.9.1"),
    "ShowProcessesCpuSorted": ({}, CPU_SORTED_OUTPUT),
    "ShowProcessesCpuPlatform": ({}, CPU_PLATFORM_OUTPUT),
    "ShowEnvironment": ({}, "Number of Critical alarms:  0"),
    "ShowProcessesCpu": ({}, CPU_SORTED_OUTPUT),
    "ShowVersionRp": ({"rp": "active", "status": "running"}, "Package: rpbase, version: 03.16.04a.S.155-3.S4a-ext, status: active\nFile: consolidated:asr1000rp2-rpbase.03.16.04a.S.155-3.S4a-ext.pkg, on: RP0"),
    "ShowPlatformPower": ({}, "Chassis type: ASR1006-X"),
    "ShowProcessesCpuHistory": ({}, "80 #\nCPU% per second (last 60 seconds)"),
    "ShowProcessesMemory": ({}, MEMORY_OUTPUT),
    "ShowProcessesMemorySorted": ({}, MEMORY_OUTPUT),
    "ShowPlatformIntegrity": ({}, "Platform: C9300-24U\nBoot 0 Version: F01144R16.216e68ad62019-02-13"),
    "ShowPlatformTcamUtilization": ({"switch": "switch", "mode": "active"}, "CAM Utilization for ASIC  [0]\nMac Address Table      EM           I       16384       44    0.27%        0        0        0       44"),
    "ShowPlatformResources": ({}, "RP0 (ok, active) H"),
    "ShowPlatformSudiCertificateNonce": ({"signature": "123"}, "-----BEGIN CERTIFICATE-----\nABC123\n-----END CERTIFICATE-----"),
    "ShowEnvironmentStatus": ({}, "Switch:1\nPS0 C9K-PWR-650WAC-R AC 650 W ok good N/A"),
    "ShowPlatformSudiPki": ({}, "Cisco Manufacturing CA              Valid"),
    "ShowPlatformTcamPbr": ({"nat_region": "NAT_1"}, "Printing entries for region NAT_1 (387) type 6 asic 0\nTAQ-1 Index-352 (A:0,C:0) Valid StartF-1 StartA-1 SkipF-0 SkipA-0\nMask1 00ffff00:00000000"),
    "ShowPlatformNatTranslationsStatistics": ({}, NAT_STATS_OUTPUT),
    "ShowPlatformNatTranslations": ({}, NAT_TRANSLATION_OUTPUT),
    "ShowPlatformTcamAcl": ({"INPUT_NAT": "INPUT_NAT"}, "Index-1152\nM: 00000000 0000 00 00 00000000 00000000 00 0000 0000 000 00"),
    "ShowVersionRunning": ({}, "Package: Provisioning File, version: n/a, status: active"),
    "ShowCallAdmissionStatistics": ({}, "CAC New Model (SRSM) is ACTIVE"),
    "ShowCallAdmissionStatisticsDetailed": ({}, "CAC New Model (SRSM) is ACTIVE"),
    "ShowRepTopologySegment": ({"no": "1"}, "fr1 Gi1/0/3 Sec* Open"),
    "ShowPlatformPacketStats": ({}, "  Matched  1"),
    "ShowPlatformPacketSumm": ({}, "0 Gi0/0/1 Gi0/0/0 FWD 97 (Packets to LFTS)"),
    "ShowPlatformPacketTracePacket": ({}, "Packet: 0           CBUG ID: 104\nSummary\n  Input     : GigabitEthernet1"),
    "ShowSystemMtu": ({}, "Global Ethernet MTU is 1500 bytes."),
    "ShowProcessesCpuPlatformSorted": ({}, CPU_PLATFORM_OUTPUT),
    "ShowFileSystems": ({}, "* 11353194496 7130390528 disk rw flash-3:"),
    "ShowRedundancyConfigSyncFailuresMcl": ({}, "The list is Empty"),
    "ShowPlatformAuthenticationSbinfoInterface": ({"interface": "Gi1/0/24"}, "  SB Access Vlan: 1"),
    "ShowPlatformHostAccessTableIntf": ({"intf": "Gi1/0/24"}, "001b.0c18.918d 100 permit dot1x dynamic"),
    "ShowPlatformPmPortDataInt": ({"interface": "Gi1/0/24"}, "   Forwarding Vlans : 100"),
    "ShowPlatformRewriteUtilization": ({}, "Resource Info for ASIC Instance: 0\nPHF_EGRESS_destMacAddress 75001 23303"),
    "ShowPlatformMatmMacTable": ({}, "HEAD: MAC address 0012.7fae.9662 in VLAN 1"),
    "ShowSwitchStackRingSpeed": ({}, "Stack Ring Speed        : 240G"),
    "ShowPlatformUsbStatus": ({}, "USB enabled"),
    "ShowPlatformPmInterfaceNumbers": ({}, "Gi1/0/1 9 1 1 1 1 0x7F2C5B930F40 0x10040 0x20001B 0x4 9"),
    "ShowProcessesPid": ({"processid": "3"}, "Process ID 3 [Network Synchronization Selection Control Process], TTY 0"),
    "ShowXfsuEligibility": ({}, "Reload fast supported: Yes"),
    "ShowSwitchStackPortsDetail": ({}, "1/1 is DOWN Loopback No"),
    "ShowXfsuStatus": ({}, "Reload Fast PLATFORM Status: Not started yet"),
    "ShowGracefulReload": ({}, "Reload Fast PLATFORM Status: Not started yet"),
    "ShowFileSys": ({"filesystem": "usbflash0"}, "Filesystem: usbflash0"),
    "ShowFileInformation": ({"file": "flash:test.pkg"}, "type is IOSXE_PACKAGE []"),
    "ShowFileDescriptorsDetail": ({}, "0 0 0000 699 revrcsf:-"),
    "ShowTimeRange": ({"time_range_name": "time1"}, "time-range entry: time1 (active)"),
    "ShowPlatformPmEtherchannelGroupMask": ({"ec_channel_group_id": "10"}, "EC Channel-Group               : 10"),
    "TestPlatformSoftwareDatabase": ({"component": "platform_component"}, "Table Record Index 0 = {\n[0] cname = Fan1/1"),
    "ShowPlatformSoftwareFedSwitchAclUsageIncludeAcl": ({"switch_num": "1"}, "PACL IPV4 Egress racl_permit_egress 2"),
    "ShowRepTopology": ({}, "REP Segment 1\nC9200_DUT Gi1/0/1 Pri* Open"),
    "ShowRepTopologyDetail": ({}, "REP Segment 50\nBOIS168ZW2001, Te0/2 (Primary Edge No-Neighbor)"),
    "ShowPlatformfrontendcontroller": ({"switch_num": "1"}, "Switch 1 MCU:"),
    "ShowPlatformNatTranslationsStandby": ({}, NAT_TRANSLATION_OUTPUT),
    "ShowPlatformNatTranslationsStandbyStatistics": ({}, NAT_STATS_OUTPUT),
    "ShowPlatformSoftwareCpmSwitchActiveB0PacketsControlIpc": ({"mode": "active", "controlmode": "ipc", "transmitmode": "tx"}, "Packet :: 1\nJun 16 13:13:17.742\nabcd"),
    "ShowPlatformUplinks": ({}, "TenGigabitEthernet4/0/6 Up"),
    "ShowPlatformSoftwareInfrastructurePunt": ({}, "enabled=0, disabled=0, throttled=0, unthrottled=0, state is ready"),
    "ShowPlatformDiag": ({}, "Chassis type: ISR4461/K9"),
    "ShowEnvironmentTemperatureAll": ({}, "Switch 3: SYSTEM TEMPERATURE is OK"),
    "ShowPlatformSoftwareWccpWebCacheCounters": ({}, "Service Group (0, 0, 0) counters"),
    "ShowXdrLinecard": ({}, "XDR slot number 1, status  PEER UP"),
    "ShowZonePairSecurity": ({}, "Zone-pair name inter-vrf-zp 1"),
    "ShowPlatformHardwareQfpActiveFeatureNatDatapathPort": ({}, "Bit stats: 1stword 217 scan 4 scanread 132"),
    "ShowPlatformHardwareQfpActiveFeatureNatDatapathMap": ({}, "edm maps 0"),
    "ShowPlatformHardwareQfpActiveFeatureNatDatapathEsp": ({}, "ESP global stats: esp_count 0  esp_limit_fail_count 0"),
    "ShowPlatformHardwareIomdEthernetControllersPhyHistogram": ({"iomd": "0", "phy": "1"}, "****** Port = 32, Phy_port = 1, Ctrl = 0 *******\nside:sideA mdioPort:1 laneOffset:0 InnerEyeHeight 0x1,[23:16] 2,OuterEyeHeight 0x3,[31:24] 4, eyerat 1.0, Status: 0"),
    "ShowPlatformManagementInterface": ({}, "Management interface is GigabitEthernet0/0"),
    "ShowPlatformHardwareSlotSenConsumerAll": ({"slot": "0"}, "Registration: Registered"),
    "ShowSystemStats": ({}, SYSTEM_STATS_OUTPUT),
    "ShowPlatformHardwareQfpActiveFeatureNat66DatapathStatistics": ({}, "in2out xlated pkts 1022"),
    "ShowPlatformSoftwareNat66RpActivePrefixTranslation": ({"nat_type": "nat66", "rp_location": "active"}, "5 2001:101:0:1::/96 2001:101:0:3::/96"),
    "ShowPlatformHardwareSubslotModuleHostIfStatistics": ({"subslot": "0/1"}, "GE (connecting to BP switch) statistics\npkt forwarded 41355 3325326 41438 3465186"),
    "ShowPlatformSoftwareInfrastructureThreadFastpath": ({}, SYSTEM_STATS_OUTPUT),
    "ShowPlatformHardwareCppActiveFeatureNatDatapathSessDump": ({}, "id 0x38c82d90 io 5.0.0.2 oo 110.1.1.1 io 49186 oo 33438 it 110.100.1.1 ot 110.1.1.1 it 49186 ot 33438 pro 17 vrf 0 tableid 0 bck 3804 in_if 10 out_if 8 ext_flags 0x0 in_pkts 1 in_bytes 8 out_pkts 0 out_bytes 0 flowdb in2out fh 0x0 flowdb out2in fh 0x0"),
    "ShowPlatformSoftwareFedIpv6RouteSummaryInclude": ({"mode": "active", "match": "Total"}, "Total number of v6 fib EM hw entries for device:0 = 2"),
}


@pytest.mark.parametrize("class_name", sorted(SHOW_PLATFORM_CASES))
def test_show_platform_parser_class(class_name: str) -> None:
    kwargs, output = SHOW_PLATFORM_CASES[class_name]
    parser = getattr(parsers, class_name)()

    parsed = parser.cli(output=output, **kwargs)

    assert parsed


def test_all_effective_show_platform_parser_classes_are_covered() -> None:
    parser_classes = {
        name
        for name, parser_class in inspect.getmembers(parsers, inspect.isclass)
        if parser_class.__module__ == parsers.__name__ and hasattr(parser_class, "cli_command")
    }

    assert parser_classes == set(SHOW_PLATFORM_CASES)


def test_show_platform_commands_are_registered() -> None:
    supported = yenie_parser.supported_commands("iosxe")

    assert "show bootvar" in supported
    assert "show platform" in supported
    assert "dir {directory}" in supported
    assert "show processes memory | section {section}" in supported
    assert "test platform software database get-n all ios_oper/{component}" in supported
    assert "show plaform software fed switch {switch_num} acl usage" in supported


def test_parse_accepts_show_platform_exact_command() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show platform",
        raw_output="Chassis type: ASR1006",
    )

    assert parsed["main"]["chassis"] == "ASR1006"


def test_parse_accepts_c9300_show_version_stack_table() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show version",
        raw_output=SHOW_VERSION_C9300_OUTPUT,
        strict=True,
    )

    version = parsed["version"]
    assert version["xe_version"] == "17.03.04"
    assert version["version"] == "17.3.4"
    assert version["hostname"] == "chi-csw-01"
    assert version["system_image"] == "flash:packages.conf"
    assert "------" not in version["switch_num"]

    switch = version["switch_num"]["1"]
    assert switch["active"] is True
    assert switch["ports"] == "41"
    assert switch["model"] == "C9300-24T"
    assert switch["sw_ver"] == "17.03.04"
    assert switch["sw_image"] == "CAT9K_IOSXE"
    assert switch["mode"] == "INSTALL"


def test_parse_accepts_show_bootvar_exact_command() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show bootvar",
        raw_output="BOOT variable = flash:image.bin;",
    )

    assert parsed["active"]["boot_variable"] == "flash:image.bin;"


def test_parse_accepts_dir_placeholder_command() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="dir flash:/",
        raw_output="Directory of flash:/",
    )

    assert parsed["dir"]["dir"] == "flash:/"


def test_parse_accepts_section_pipe_placeholder_command() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show processes memory | section Init",
        raw_output=MEMORY_OUTPUT,
    )

    assert parsed["processor_pool"]["total"] == 10147887840


def test_parse_accepts_embedded_placeholder_command() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="test platform software database get-n all ios_oper/platform_component",
        raw_output="Table Record Index 0 = {\n[0] cname = Fan1/1",
    )

    assert parsed["table_record_index"]["0"]["cname"] == "Fan1/1"


def test_parse_preserves_upstream_typo_template() -> None:
    parsed = yenie_parser.parse(
        platform="iosxe",
        command="show plaform software fed switch 1 acl usage",
        raw_output="PACL IPV4 Egress racl_permit_egress 2",
    )

    assert parsed["entries_used"] == 2
