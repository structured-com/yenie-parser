# Genie Parser Conversion: IOS-XE show_arp.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_arp.py`
- Upstream branch/ref used: `main`
- Upstream commit SHA: `b4b31e251b2c40ab92b9849ed985a02e647ef27c`
- Conversion date: 2026-05-28
- Local module: `yenie_parser.iosxe._genie_show_arp`

## File Notes

- The upstream parser includes ARP, `show ip traffic`, adjacency summary, and
  ARP inspection command parsers in one file; Yenie Parser keeps the same
  effective parser set.

## Supported Command Templates

- `show arp`
- `show arp vrf {vrf}`
- `show arp vrf {vrf} {intf_or_ip}`
- `show arp {intf_or_ip}`
- `show ip arp`
- `show ip arp vrf {vrf}`
- `show ip arp summary`
- `show ip traffic`
- `show arp application`
- `show arp summary`
- `show ip arp inspection vlan {num}`
- `show adjacency summary`
- `show ip arp inspection statistics vlan {num}`
- `show ip arp inspection interfaces {interface}`
- `show ip arp inspection log`
