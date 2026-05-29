# Genie Parser Conversion: IOS-XE show_aaa.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_aaa.py`
- Upstream branch/ref used: `b4b31e251b2c40ab92b9849ed985a02e647ef27c`
- Upstream commit SHA: `b4b31e251b2c40ab92b9849ed985a02e647ef27c`
- Conversion date: 2026-05-29
- Local module: `yenie_parser.iosxe._genie_show_aaa`

## File Notes

- All effective upstream parser classes with `cli_command` are dispatchable.
- `ShowAaaDeadCriteriaRadius` is adapted so caller-provided raw output is parsed without requiring device execution.

## Supported Command Templates

- `show aaa servers`
- `show aaa user all`
- `show aaa fqdn all`
- `show aaa cache group {server_grp} all`
- `show aaa cache group {server_grp} profile {profile}`
- `show aaa common-criteria policy name {policy_name}`
- `show aaa method-lists {type}`
- `show aaa dead-criteria radius {server_ip}`
- `show aaa dead-criteria radius {server_ip} auth-port {auth_port} acct-port {acct_port}`
- `show aaa dead-criteria radius server-name {server_name}`
- `show aaa sessions`
- `show aaa memory`
