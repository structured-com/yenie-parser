# Yenie Parser

Yenie Parser is a small Python package for parsing Cisco CLI command output into
structured dictionaries without importing the full Cisco Genie/pyATS stack.

The IOS-XE parser set covers command templates adapted from Cisco Genie parser
files. Results use Genie-compatible dictionary shapes where the upstream parser
defines them.

## Install

This package is intended to work with normal Python packaging tools once
published:

```bash
pip install yenie-parser
```

For local development with uv:

```bash
uv sync
uv run pytest
```

## Usage

```python
import yenie_parser

parsed = yenie_parser.parse(
    platform="iosxe",
    command="show device-tracking database",
    raw_output=raw_cli_output,
)
```

The parser accepts only raw command output. It does not connect to devices or
execute commands.

Command matching strips extra whitespace and is case-insensitive. It does not
rewrite Cisco command tokens, so `device-tracking` and `device tracking` are
different commands.

Available command templates can be inspected with:

```python
commands = yenie_parser.supported_commands("iosxe")
```

## Attribution

Parser behavior is derived from the Apache-2.0 licensed Cisco Genie parser
project:

- Repository: https://github.com/CiscoTestAutomation/genieparser
- Source paths:
  - `src/genie/libs/parser/iosxe/show_device_tracking.py`
  - `src/genie/libs/parser/iosxe/show_authentication_sessions.py`
  - `src/genie/libs/parser/iosxe/show_inventory.py`
  - `src/genie/libs/parser/iosxe/show_cdp.py`
  - `src/genie/libs/parser/iosxe/show_arp.py`
  - `src/genie/libs/parser/iosxe/show_fdb.py`
  - `src/genie/libs/parser/iosxe/show_interface.py`
  - `src/genie/libs/parser/iosxe/show_run.py`

See `docs/conversions/` for conversion metadata.
