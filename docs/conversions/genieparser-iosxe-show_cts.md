# Genie Parser Conversion: IOS-XE show_cts.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_cts.py`
- Upstream branch/ref used: `fe78fb29ac3c9e44a854ff34beb72d4ec9242bb0`
- Upstream commit SHA: `fe78fb29ac3c9e44a854ff34beb72d4ec9242bb0`
- Conversion date: 2026-05-29
- Local module: `yenie_parser.iosxe._genie_show_cts`

## File Notes

- All effective upstream parser classes with `cli_command` are dispatchable.
- `genie.parsergen.oper_fill_tabular` is replaced by a small local compatibility shim.
- Device execution paths are inert when direct parser calls omit `output`; registry dispatch always supplies raw output.
- The upstream file has 26 effective parser classes with `cli_command`.

## Supported Command Templates

- `show cts sxp connections brief`
- `show cts pacs`
- `show cts role-based counters`
- `show cts role-based counters {ipv4}`
- `show cts role-based counters {ipv6}`
- `show cts role-based counters {default}`
- `show cts role-based counters {default} {ipv4}`
- `show cts role-based counters {default} {ipv6}`
- `show cts role-based counters from {from_sgt}`
- `show cts role-based counters from {from_sgt} {ipv4}`
- `show cts role-based counters from {from_sgt} {ipv6}`
- `show cts role-based counters from {from_sgt} to {to_sgt}`
- `show cts role-based counters from {from_sgt} to {to_sgt} {ipv4}`
- `show cts role-based counters from {from_sgt} to {to_sgt} {ipv6}`
- `show cts role-based counters from {to_sgt}`
- `show cts role-based counters from {to_sgt} {ipv4}`
- `show cts role-based counters from {to_sgt} {ipv6}`
- `show cts`
- `show cts environment-data`
- `show cts rbacl`
- `show cts role-based permissions`
- `show cts role-based permissions {ipv4}`
- `show cts role-based permissions {ipv6}`
- `show cts role-based permissions {default}`
- `show cts role-based permissions {default} {ipv4}`
- `show cts role-based permissions {default} {ipv6}`
- `show cts role-based permissions from {from_sgt}`
- `show cts role-based permissions from {from_sgt} {ipv4}`
- `show cts role-based permissions from {from_sgt} {ipv6}`
- `show cts role-based permissions from {from_sgt} to {to_sgt}`
- `show cts role-based permissions from {from_sgt} to {to_sgt} {ipv4}`
- `show cts role-based permissions from {from_sgt} to {to_sgt} {ipv6}`
- `show cts role-based permissions from {to_sgt}`
- `show cts role-based permissions from {to_sgt} {ipv4}`
- `show cts role-based permissions from {to_sgt} {ipv6}`
- `show cts wireless profile policy {policy}`
- `show cts ap sgt info {ap_name}`
- `show cts interface`
- `show cts interface {interface}`
- `show cts role-based sgt-map {ip}`
- `show cts role-based sgt-map vrf {vrf} {ip}`
- `show cts role-based sgt-map all`
- `show cts role-based sgt-map vrf {vrf} all`
- `show cts sxp connections`
- `show cts sxp connections vrf {vrf}`
- `show cts sxp sgt-map brief`
- `show cts sxp sgt-map vrf {vrf} brief`
- `show cts server-list`
- `show cts policy-server statistics all`
- `show cts policy-server statistics active`
- `show cts policy-server statistics name {server_name}`
- `show cts policy-server details all`
- `show cts policy-server details active`
- `show cts policy-server details name {server_name}`
- `show platform software fed {instance} acl sgacl cell all`
- `show platform software fed {switch} {instance} acl sgacl cell all`
- `show cts interface summary`
- `show cts policy sgt {sgt}`
- `show cts ha sync-status`
- `show cts provisioning queue`
- `show cts credentials`
- `show cts sxp sgt-map`
- `show cts sxp sgt-map vrf {vrf}`
- `show cts sxp export-import-group {role} detailed`
- `show cts keystore`
