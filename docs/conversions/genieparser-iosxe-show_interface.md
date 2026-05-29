# Genie Parser Conversion: IOS-XE show_interface.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_interface.py`
- Upstream branch/ref used: `3e6c8c1d099f623c891185942f038f940acd395b`
- Upstream commit SHA: `3e6c8c1d099f623c891185942f038f940acd395b`
- Conversion date: 2026-05-29
- Local module: `yenie_parser.iosxe._genie_show_interface`

## File Notes

- `ShowIpInterfaceBrief` uses local raw-text table parsing instead of Genie
  `parsergen`.
- `ShowIpInterfaceBriefPipeVlan`, `ShowInterfacesMtu`, and
  `ShowInterfacesStatusModule` were adjusted to honor provided raw output.
- `ShowInterfaceTeAccount` is retained as non-dispatchable adapted source
  because upstream does not define `cli_command` for it.

## Supported Command Templates

- `show interfaces`
- `show interfaces {interface}`
- `show interfaces | include {include}`
- `show ip interface brief {interface}`
- `show ip interface brief`
- `show ip interface brief | include Vlan`
- `show ip interface brief | include {ip}`
- `show interfaces switchport`
- `show interfaces {interface} switchport`
- `show ip interface`
- `show ip interface {interface}`
- `show ip interface | include {include}`
- `show ipv6 interface`
- `show ipv6 interface {interface}`
- `show ipv6 interface | include {include}`
- `show interfaces trunk`
- `show interfaces {interface} trunk`
- `show interfaces {interface} counters`
- `show interfaces {interface} counter etherchannel`
- `show interfaces {interface} accounting`
- `show interfaces accounting`
- `show interfaces link`
- `show interfaces {interface} link`
- `show interfaces stats`
- `show interfaces {interface} stats`
- `show interfaces description`
- `show interfaces {interface} description`
- `show interfaces status`
- `show interfaces {interface} status`
- `show interfaces status err-disabled`
- `show interfaces {interface} transceiver detail`
- `show interfaces transceiver detail`
- `show interfaces {interface} transceiver`
- `show interfaces transceiver`
- `show macro auto interface {interface}`
- `show macro auto interface`
- `show interface summary vlan`
- `show interfaces summary`
- `show interfaces {interface} summary`
- `show interfaces mtu`
- `show interfaces {interface} mtu`
- `show interfaces mtu module {mod}`
- `show interfaces status module {mod}`
- `show pm vp interface {interface} {vlan}`
- `show interfaces transceiver supported-list`
- `show pm port interface {interface}`
- `show interfaces private-vlan mapping`
- `show interface {interface_id} etherchannel`
- `show interfaces capabilities`
- `show interfaces {interface} capabilities`
- `show interfaces {interface_id} flowcontrol`
- `show interface {interface} vlan mapping`
- `show interface {interface} human-readable | i drops`
- `show interface {interface} human-readable`
- `show interfaces transceiver properties`
- `show interfaces transceiver module {mod}`
- `show interface {interface} platform`
- `show interfaces {interface} mac-accounting`
- `show interfaces mac-accounting`
