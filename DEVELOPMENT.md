# Yenie Parser Development Guide

This guide is the main reference for developers and AI coding agents working on
Yenie Parser.

## Project Purpose

Yenie Parser parses raw Cisco CLI command output into structured dictionaries
without importing Cisco Genie, pyATS, or device connection machinery.

The public API is:

```python
import yenie_parser

parsed = yenie_parser.parse(
    platform="iosxe",
    command="show device-tracking database",
    raw_output=raw_cli_output,
)
```

Runtime parsing must operate from raw multiline text only. It must not connect
to devices, execute commands, import Genie/pyATS, or require platform-specific
dependencies.

## Package Layout

- `src/yenie_parser/__init__.py`: public API exports.
- `src/yenie_parser/_registry.py`: platform/command dispatch.
- `src/yenie_parser/exceptions.py`: public exception types.
- `src/yenie_parser/_genie_compat.py`: small compatibility shims used by adapted Genie parser code.
- `src/yenie_parser/iosxe/_genie_*.py`: internal IOS-XE parser modules adapted from Genie source files.
- `docs/conversions/*.md`: slim source-tracking records for each converted upstream Genie file.
- `tests/`: API, registry behavior, and parser fixture tests.

The package uses `uv_build` in `pyproject.toml` and a `src/` layout. Development
uses uv:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync
UV_CACHE_DIR=/tmp/uv-cache uv run pytest
UV_CACHE_DIR=/tmp/uv-cache uv run ruff check src tests
UV_CACHE_DIR=/tmp/uv-cache uv build
```

## Public API And Dispatch

`yenie_parser.parse(platform, command, raw_output)` dispatches to an internal
parser class through `ParserEntry` records in `_registry.py`.

Command matching rules:

- Platform is stripped and lowercased.
- Command text is stripped, repeated whitespace is collapsed, and matching is case-insensitive.
- Hyphens are not normalized. `device-tracking` and `device tracking` are different Cisco command tokens.
- Registered templates and concrete command strings are both accepted.
- Placeholder tokens such as `{interface}` and `{mac}` match non-whitespace command values.
- Pipe suffix placeholders such as `| section {message}` and `| count {match}` capture trailing text.
- Overlapping templates are ordered by exact-template match, literal-token count, template length, and source order.

Unsupported platforms raise `UnsupportedPlatformError`; unsupported commands
raise `UnsupportedCommandError`; unresolved equal-specificity matches can raise
`AmbiguousCommandError`.

## How Adapted Genie Modules Are Built

Each internal `_genie_*.py` module represents one upstream Genie parser file.
The current modules are:

- `src/yenie_parser/iosxe/_genie_show_device_tracking.py`
- `src/yenie_parser/iosxe/_genie_show_authentication_sessions.py`

These modules are adapted source, not normal handwritten application modules.
Their job is to preserve upstream parser behavior while removing Genie runtime
dependencies.

Each module should contain:

- A `# ruff: noqa` header because adapted upstream code may not match local style.
- Source constants:
  - `GENIE_SOURCE_REPOSITORY`
  - `GENIE_SOURCE_PATH`
  - `GENIE_SOURCE_REF`
  - `GENIE_SOURCE_COMMIT`
- Parser classes with `cli_command` attributes and `cli(..., output=None)` methods.
- A module-level `SUPPORTED_COMMANDS` tuple listing all effective command templates.

When adapting a new Genie parser file:

1. Fetch the upstream raw file and latest commit SHA for that path.
2. Copy the relevant parser classes into a new internal module named `_genie_<source_stem>.py`.
3. Replace Genie imports with local compatibility imports from `yenie_parser._genie_compat`.
4. Keep parser return shapes Genie-compatible unless intentionally documented otherwise.
5. Remove live device execution from the runtime path by ensuring `output` is passed into every parser from the registry.
6. Fix any upstream code path that assumes `self.device` or leaves an `out` variable undefined when `output` is provided.
7. Preserve all effective `cli_command` templates. If upstream defines a class name more than once, keep the effective later class behavior.
8. Add source constants and `SUPPORTED_COMMANDS`.
9. Add a slim file in `docs/conversions/` with source metadata, supported templates, and file-specific notes.
10. Add tests for every effective parser class in the module.
11. Confirm the new templates appear in `yenie_parser.supported_commands("iosxe")`.

Avoid broad refactors inside adapted modules. If shared behavior is needed,
prefer small helpers in `_genie_compat.py` or `_registry.py`.

## Compatibility Shims

`_genie_compat.py` replaces only the small subset of Genie APIs needed by
adapted parser code:

- `MetaParser`
- schema declaration placeholders such as `Any`, `Optional`, `Or`, `ListOf`
- `Schema`, `And`, `Default`, `Use`
- `Common.convert_intf_name`

The schema shims are intentionally non-validating. They exist so class-level
schema declarations can import and evaluate without pulling in Genie.

`Common.convert_intf_name` is intentionally limited. Extend it only when tests
or real parser outputs show an interface abbreviation that should be expanded.

## Tests

Tests should cover three layers:

- Public API tests in `tests/test_api.py`.
- One representative positive fixture for every effective parser class in each adapted module.
- Empty or unmatched output behavior where the parser is intended to be permissive.

For new parser files, add a test module named after the upstream source file,
for example `tests/iosxe/test_show_<topic>.py`. Include a coverage assertion
that compares the set of parser classes with `cli_command` attributes against
the fixture cases so future adapted classes are not silently untested.

## Conversion Docs

Keep `docs/conversions/*.md` slim. Each file should record:

- Upstream repository.
- Upstream source path.
- Upstream ref and commit SHA.
- Conversion date.
- Local internal module.
- Supported command templates.
- File-specific notes only.

Do not repeat the general conversion workflow or standard Genie-removal notes
inside each conversion file; keep that content here.

## Release And Build Notes

The package is PyPI-ready but publishing is manual. Build artifacts are created
with:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv build
```

Smoke test a wheel with uv:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run --with dist/yenie_parser-<version>-py3-none-any.whl --no-project python -c "import yenie_parser; print(yenie_parser.supported_commands('iosxe'))"
```

Smoke test with pip in a clean venv:

```bash
python -m venv /tmp/yenie-parser-pip-venv
/tmp/yenie-parser-pip-venv/bin/python -m pip install dist/yenie_parser-<version>-py3-none-any.whl
/tmp/yenie-parser-pip-venv/bin/python -c "import yenie_parser; print(yenie_parser.__version__)"
```

If rebuilding the same version repeatedly, uv may reuse a cached wheel. Prefer
bumping the version for meaningful API/package changes.
