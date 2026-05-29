# Genie Parser Conversion: IOS-XE show_fdb.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_fdb.py`
- Upstream branch/ref used: `main`
- Upstream commit SHA: `b4b31e251b2c40ab92b9849ed985a02e647ef27c`
- Conversion date: 2026-05-28
- Local module: `yenie_parser.iosxe._genie_show_fdb`

## File Notes

- The upstream file has duplicated Genie import blocks; Yenie Parser replaces
  them with one local compatibility import.

## Supported Command Templates

- `show mac address-table`
- `show mac address-table vlan {vlan}`
- `show mac address-table interface {interface}`
- `show mac address-table interface {interface} vlan {vlan}`
- `show mac address-table aging-time`
- `show mac address-table learning`
- `show mac address-table address {mac} vlan {vlan}`
- `show mac address-table notification change`
- `show mac address-table notification change interface {interface}`
