# Genie Parser Conversion: IOS-XE show_inventory.py

## Source

- Upstream repository: https://github.com/CiscoTestAutomation/genieparser
- Upstream source path: `src/genie/libs/parser/iosxe/show_inventory.py`
- Upstream branch/ref used: `main`
- Upstream commit SHA: `ab7e69ffaeb0e5e78dfb6e7ea69ac33d2ea0591a`
- Conversion date: 2026-05-28
- Local module: `yenie_parser.iosxe._genie_show_inventory`

## File Notes

- The upstream module comment says `show incentory OID`; Yenie Parser corrects
  the spelling to `show inventory OID`.

## Supported Command Templates

- `show inventory raw | include {include}`
- `show inventory raw`
- `show inventory OID`
- `show inventory "{name}"`
