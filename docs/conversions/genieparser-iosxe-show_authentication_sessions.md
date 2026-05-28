# Genie Parser Conversion: IOS-XE show_authentication_sessions.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_authentication_sessions.py`
- Upstream branch/ref used: `main`
- Upstream commit SHA: `07d9c0fd6fba168086b86bd4a38ca4037fbd5c19`
- Conversion date: 2026-05-28
- Local module: `yenie_parser.iosxe._genie_show_authentication_sessions`

## File Notes

- This upstream file includes `authentication display config-mode`, which is
  not a `show` command. Yenie Parser registers it because it is present in the
  upstream `cli_command` declarations.
- `show authentication sessions interface {interface}` appears in more than
  one upstream parser class. Registry specificity and result fallback select a
  usable parser for concrete raw output.

## Supported Command Templates

- `show authentication sessions`
- `show authentication sessions interface {interface}`
- `show authentication sessions interface {interface} details`
- `show authentication sessions interface {interface} details switch {switch} r0`
- `show authentication sessions mac {mac_address} details`
- `show authentication sessions mac {mac_address} details switch {switch} r0`
- `authentication display config-mode`
- `show access-session info`
- `show access-session info switch {sw} r0`
- `show authentication sessions switch {switch} R0`
- `show access-session mac {mac} switch {switch} R0`
- `show authentication sessions mac {mac} details`
- `show authentication sessions mac {mac} interface {interface} details`
- `show authentication sessions mac {mac} method {method} details`
- `show authentication sessions mac {mac} method {method} details switch {switch} R0`
- `show authentication sessions mac {mac} policy`
- `show authentication sessions interface {interface} {details}`
- `show authentication sessions interface {interface} {policy}`
- `show authentication sessions interface {interface} {details} switch {switch} R0`
- `show authentication sessions interface {interface} {policy} switch {switch} R0`
- `show authentication sessions {database} interface {interface} {details}`
- `show authentication sessions {database} interface {interface} {policy}`
- `show authentication sessions {database} interface {interface} {policy} switch {switch} R0`
- `show authentication sessions session-id {session_id} details`
- `show authentication sessions session-id {session_id} policy`
- `show authentication sessions session-id {session_id} switch active R0`
- `show authentication sessions interface {interface} switch {switch} R0`
- `show authentication sessions {database} interface {interface} switch {switch} R0`
- `show authentication sessions method {method} {details}`
- `show authentication sessions method {method} interface {interface} details`
