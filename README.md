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

### Python API

```python
import yenie_parser

parsed = yenie_parser.parse(
    platform="iosxe",
    command="show device-tracking database",
    raw_output=raw_cli_output,
)
```

### CLI

The installed package provides a `yenie-parser` terminal command:

```bash
yenie-parser parse \
  --platform iosxe \
  --command "show device-tracking database" \
  --raw-output "Binding Table has 1 entries, 0 dynamic (limit 200000)"
```

Multiline command output can also be read from a file or stdin:

```bash
yenie-parser parse -p iosxe -c "show device-tracking database" --raw-file output.txt
cat output.txt | yenie-parser parse -p iosxe -c "show device-tracking database"
```

Parser failure behavior mirrors the Python API:

```bash
yenie-parser parse \
  -p iosxe \
  -c "show device-tracking database" \
  --raw-file output.txt \
  --strict \
  --warn \
  --on-failure none
```

Supported parser templates can be listed or searched:

```bash
yenie-parser list
yenie-parser list "authentication s"
yenie-parser list --search "authentication s"
yenie-parser list --command "show authentication sessions"
```

Package metadata is available with:

```bash
yenie-parser --version
```

Currently, parser supports these platforms:
- `iosxe`

The parser accepts only raw command output. It does not connect to devices or
execute commands.

By default, `parse(...)` returns `None` when parsing fails. That includes
unsupported platforms, unsupported commands, ambiguous command matches, parser
execution failures, and raw output that matches a command but produces no
structured data.

Failure behavior can be adjusted for strict validation, warnings, or legacy
fallback values:

```python
parsed = yenie_parser.parse(
    platform="iosxe",
    command="show device-tracking database",
    raw_output=raw_cli_output,
    strict=False,
    warn=False,
    on_failure="none",
)
```

Supported `on_failure` values are:

- `"none"`: return `None` on failure. This is the default.
- `"empty_dict"`: return `{}` on failure for legacy callers.
- `"raw_output"`: return the original `raw_output` string on failure.

When `strict=True`, parse failures raise Yenie Parser exceptions instead of
returning the configured `on_failure` value. When `warn=True`, parse failures
emit a standard-library warning using `YenieParserWarning`.

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
  - `src/genie/libs/parser/iosxe/show_routing.py`
  - `src/genie/libs/parser/iosxe/show_aaa.py`
  - `src/genie/libs/parser/iosxe/show_cts.py`

See `docs/conversions/` for conversion metadata.
