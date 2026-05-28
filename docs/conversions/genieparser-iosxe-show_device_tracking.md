# Genie Parser Conversion: IOS-XE show_device_tracking.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_device_tracking.py`
- Upstream branch/ref used: `main`
- Upstream commit SHA: `fe78fb29ac3c9e44a854ff34beb72d4ec9242bb0`
- Conversion date: 2026-05-28
- Local module: `yenie_parser.iosxe._genie_show_device_tracking`

## File Notes

- Upstream defines `ShowDeviceTrackingDatabaseDetails` twice; Yenie Parser keeps
  the effective later implementation, which also supports interface and VLAN
  detail variants.
- The adapted detail parser assigns `out = output` for raw-output parsing,
  because the upstream later implementation otherwise references `out` only
  after the device-execution branch.

## Supported Command Templates

- `show device-tracking database`
- `show device-tracking database vlan {vlan_id}`
- `show device-tracking database address {address}`
- `show device-tracking database interface {interface}`
- `show device-tracking policies`
- `show device-tracking policies interface {interface}`
- `show device-tracking policies vlan {vlan}`
- `show device-tracking policy {policy_name}`
- `show ipv6 nd raguard policy {policy_name}`
- `show ipv6 source-guard policy {policy_name}`
- `show device-tracking counters vlan {vlanid}`
- `show device-tracking database mac`
- `show device-tracking database mac {mac}`
- `show device-tracking database mac {mac} details`
- `show device-tracking counters interface {interface}`
- `show device-tracking events`
- `show device-tracking features`
- `show device-tracking database mac details`
- `show device-tracking messages`
- `show device-tracking messages | section {message}`
- `show device-tracking database interface {interface} | count {match}`
- `show device-tracking capture-policy`
- `show device-tracking capture-policy interface {interface_name}`
- `show device-tracking capture-policy vlan {vlan_id}`
- `show device-tracking database details`
- `show device-tracking database interface {interface_name} details`
- `show device-tracking database vlan {vlan_id} details`
- `show device-tracking messages detailed {number}`
