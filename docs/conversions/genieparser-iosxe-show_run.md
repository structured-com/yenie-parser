# Genie Parser Conversion: IOS-XE show_run.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_run.py`
- Upstream branch/ref used: `96b1d205a28b16978fad840f5c080d2924efb548`
- Upstream commit SHA: `96b1d205a28b16978fad840f5c080d2924efb548`
- Conversion date: 2026-05-29
- Local module: `yenie_parser.iosxe._genie_show_run`

## File Notes

- All effective upstream parser classes with `cli_command` are dispatchable.
- Schema-only classes are retained as adapted source but are not registered.

## Supported Command Templates

- `show run policy-map {name}`
- `show running-config interface {interface}`
- `show running-config | section ^interface`
- `show running-config all | section ^interface`
- `show running-config mdns-sd`
- `show running-config all | sec {interface}`
- `show running-config aaa user-name`
- `show running-config aaa username`
- `show running-config flow monitor`
- `show running-config aaa`
- `show running-config nve`
- `show running-config | section route`
- `show running-config | section bgp`
- `show running-config | section vrf definition`
- `show running-config | section mac address`
- `show running-config all | section class {class_map}`
- `show running-config aaa radius-server`
- `show running-config vrf`
- `show running-config all | section alarm`
