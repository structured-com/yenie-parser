# Genie Parser Conversion: IOS-XE show_routing.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_routing.py`
- Upstream branch/ref used: `3e6c8c1d099f623c891185942f038f940acd395b`
- Upstream commit SHA: `3e6c8c1d099f623c891185942f038f940acd395b`
- Conversion date: 2026-05-29
- Local module: `yenie_parser.iosxe._genie_show_routing`

## File Notes

- All effective upstream parser classes with `cli_command` are dispatchable.
- Internal route parser classes with `parser_command` are retained for distributor behavior but are not registered directly.
- Distributor classes call local helper parser `cli(..., output=...)` methods instead of Genie `parse()` or `self.device`.

## Supported Command Templates

- `show ip route vrf {vrf}`
- `show ip route vrf {vrf} {route}`
- `show ip route vrf {vrf} {protocol}`
- `show ip route`
- `show ip route {route}`
- `show ip route {protocol}`
- `show ipv6 route vrf {vrf}`
- `show ipv6 route vrf {vrf} {route}`
- `show ipv6 route vrf {vrf} {protocol}`
- `show ipv6 route`
- `show ipv6 route {route}`
- `show ipv6 route {protocol}`
- `show ipv6 route interface {interface}`
- `show ipv6 route vrf {vrf} interface {interface}`
- `show ipv6 route vrf {vrf} updated`
- `show ipv6 route updated`
- `show ip cef`
- `show ip cef vrf {vrf}`
- `show ip cef {prefix}`
- `show ip cef vrf {vrf} {prefix}`
- `show ipv6 cef`
- `show ipv6 cef vrf {vrf}`
- `show ipv6 cef {prefix}`
- `show ipv6 cef vrf {vrf} {prefix}`
- `show ip cef {prefix} detail`
- `show ip route summary`
- `show ip route vrf {vrf} summary`
- `show ip cef {ip} internal`
- `show ip cef internal`
- `show ip cef vrf {vrf} {ip} internal`
- `show ipv6 cef {ip} internal`
- `show ipv6 cef internal`
- `show ipv6 cef vrf {vrf} {ip} internal`
- `show ipv6 route summary`
- `show ipv6 route vrf {vrf} summary`
- `show ip route vrf {vrf} supernets-only`
- `show ip route supernets-only`
- `show rib client`
- `show banner motd`
