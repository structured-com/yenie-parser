# Genie Parser Conversion: IOS-XE show_cdp.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_cdp.py`
- Upstream branch/ref used: `main`
- Upstream commit SHA: `047f0a6d6cccb0d9564682457b0ed9a371494e4a`
- Conversion date: 2026-05-28
- Local module: `yenie_parser.iosxe._genie_show_cdp`

## File Notes

- The Genie-only `parsergen` import is omitted because the adapted parser does
  not use it.
- `Common.convert_intf_name` in the local compatibility shim accepts Genie's
  `intf=` keyword form used by this parser file.

## Supported Command Templates

- `show cdp neighbors`
- `show cdp neighbors {interface}`
- `show cdp neighbors detail`
- `show cdp neighbors {interface} detail`
- `show cdp traffic`
- `show cdp interface`
- `show cdp entry {entry}`
- `show cdp entry *`
- `show cdp`
