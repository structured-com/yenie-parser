"""Command line interface for Yenie Parser."""

from __future__ import annotations

import sys
import tomllib
import warnings
from importlib.metadata import PackageNotFoundError, metadata, requires
from pathlib import Path
from typing import Any

import click
import yenie_parser
from rich.console import Console
from rich.pretty import Pretty
from rich.table import Table

from yenie_parser import _registry
from yenie_parser.exceptions import YenieParserError, YenieParserWarning

_PACKAGE_NAME = "yenie-parser"
_ON_FAILURE_VALUES = ("none", "empty_dict", "raw_output")


def _console(*, stderr: bool = False, width: int | None = None) -> Console:
    return Console(stderr=stderr, width=width)


def _print_version(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return

    info = _project_info()
    table = Table(title="Yenie Parser", show_header=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    for key, label in (
        ("name", "Name"),
        ("version", "Version"),
        ("description", "Description"),
        ("requires_python", "Requires Python"),
        ("license", "License"),
        ("keywords", "Keywords"),
        ("dependencies", "Dependencies"),
    ):
        value = info.get(key)
        if value:
            table.add_row(label, value)

    _console().print(table)
    ctx.exit()


@click.group(invoke_without_command=True)
@click.option(
    "-v",
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_print_version,
    help="Show package version and metadata.",
)
@click.pass_context
def main(ctx: click.Context) -> None:
    """Parse Cisco CLI command output."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit()


@main.command()
@click.option("-p", "--platform", required=True, help="Parser platform, for example iosxe.")
@click.option("-c", "--command", "command_text", required=True, help="Cisco command text.")
@click.option("-r", "--raw-output", help="Raw multiline command output.")
@click.option(
    "--raw-file",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="File containing raw command output.",
)
@click.option(
    "-s",
    "--strict/--no-strict",
    default=False,
    help="Raise parser failures as CLI errors.",
)
@click.option(
    "-w",
    "--warn/--no-warn",
    default=False,
    help="Print parser warnings for failures.",
)
@click.option(
    "--on-failure",
    type=click.Choice(_ON_FAILURE_VALUES),
    default="none",
    show_default=True,
    help="Fallback value for non-strict parse failures.",
)
def parse(
    platform: str,
    command_text: str,
    raw_output: str | None,
    raw_file: Path | None,
    strict: bool,
    warn: bool,
    on_failure: _registry.OnFailure,
) -> None:
    """Parse raw command output."""
    raw_text = _read_raw_output(raw_output=raw_output, raw_file=raw_file)
    console = _console()
    error_console = _console(stderr=True)
    caught_warnings: list[warnings.WarningMessage] = []

    try:
        with warnings.catch_warnings(record=True) as caught:
            caught_warnings = caught
            warnings.simplefilter("always", YenieParserWarning)
            parsed = yenie_parser.parse(
                platform=platform,
                command=command_text,
                raw_output=raw_text,
                strict=strict,
                warn=warn,
                on_failure=on_failure,
            )
    except YenieParserError as exc:
        _print_warnings(caught_warnings, error_console)
        error_console.print(f"[bold red]Error:[/bold red] {exc}")
        raise click.exceptions.Exit(1) from exc

    _print_warnings(caught_warnings, error_console)
    console.print(Pretty(parsed, expand_all=True))


@main.command(name="list")
@click.argument("query", required=False)
@click.option("-p", "--platform", default="iosxe", show_default=True, help="Parser platform.")
@click.option("--search", "search_text", help="Search command templates.")
@click.option("--command", "command_text", help="Find parser rows matching a command.")
def list_commands(
    query: str | None,
    platform: str,
    search_text: str | None,
    command_text: str | None,
) -> None:
    """List supported parser commands."""
    if command_text and (query or search_text):
        raise click.UsageError("--command cannot be combined with search text.")
    if query and search_text:
        raise click.UsageError("Use either positional search text or --search, not both.")

    entries = _matching_entries(
        platform=platform,
        search_text=query or search_text,
        command_text=command_text,
    )
    table = Table(title=f"Supported Commands ({_registry.normalize_platform(platform)})")
    table.add_column("Platform", style="bold", no_wrap=True)
    table.add_column("Command", overflow="fold")
    table.add_column("Filename", no_wrap=True)

    for entry in entries:
        table.add_row(entry.platform, entry.template, _parser_filename(entry))

    console = _console(width=120)
    console.print(table)
    if not entries:
        console.print("[yellow]No commands found.[/yellow]")


def _read_raw_output(*, raw_output: str | None, raw_file: Path | None) -> str:
    if raw_output is not None and raw_file is not None:
        raise click.UsageError("Use only one of --raw-output or --raw-file.")
    if raw_output is not None:
        return raw_output
    if raw_file is not None:
        return raw_file.read_text()
    if not sys.stdin.isatty():
        return click.get_text_stream("stdin").read()
    raise click.UsageError("Provide raw output with --raw-output, --raw-file, or stdin.")


def _matching_entries(
    *,
    platform: str,
    search_text: str | None,
    command_text: str | None,
) -> tuple[_registry.ParserEntry, ...]:
    if command_text:
        matches = _registry.find_matches(platform, command_text)
        if not matches:
            return ()
        best_score = matches[0].score
        return tuple(match.entry for match in matches if match.score == best_score)

    entries = _registry.get_registry(platform)
    if not search_text:
        return entries

    needle = _registry.normalize_command(search_text).casefold()
    return tuple(entry for entry in entries if needle in entry.normalized_template.casefold())


def _parser_filename(entry: _registry.ParserEntry) -> str:
    source_file = getattr(sys.modules.get(entry.parser_class.__module__), "__file__", None)
    if source_file:
        return Path(source_file).name
    return f"{entry.parser_class.__module__.rpartition('.')[2]}.py"


def _print_warnings(
    caught_warnings: list[warnings.WarningMessage],
    console: Console,
) -> None:
    for warning in caught_warnings:
        console.print(f"[yellow]Warning:[/yellow] {warning.message}")


def _project_info() -> dict[str, str]:
    if project_info := _pyproject_info():
        return project_info
    return _installed_project_info()


def _pyproject_info() -> dict[str, str]:
    for path in _pyproject_candidates():
        if not path.is_file():
            continue
        with path.open("rb") as pyproject_file:
            pyproject = tomllib.load(pyproject_file)
        project = pyproject.get("project", {})
        if project.get("name") != _PACKAGE_NAME:
            continue
        project_version = _string_value(project.get("version"))
        return {
            "name": _string_value(project.get("name")),
            "version": yenie_parser.__version__ if project_version else "",
            "description": _string_value(project.get("description")),
            "requires_python": _string_value(project.get("requires-python")),
            "license": _string_value(project.get("license")),
            "keywords": _sequence_value(project.get("keywords")),
            "dependencies": _sequence_value(project.get("dependencies")),
        }
    return {}


def _installed_project_info() -> dict[str, str]:
    try:
        package_metadata = metadata(_PACKAGE_NAME)
    except PackageNotFoundError:
        return {"name": _PACKAGE_NAME, "version": yenie_parser.__version__}

    return {
        "name": package_metadata.get("Name", _PACKAGE_NAME),
        "version": package_metadata.get("Version", yenie_parser.__version__),
        "description": package_metadata.get("Summary", ""),
        "requires_python": package_metadata.get("Requires-Python", ""),
        "license": package_metadata.get("License-Expression", package_metadata.get("License", "")),
        "keywords": package_metadata.get("Keywords", ""),
        "dependencies": _sequence_value(requires(_PACKAGE_NAME) or ()),
    }


def _pyproject_candidates() -> tuple[Path, ...]:
    return (
        Path.cwd() / "pyproject.toml",
        Path(__file__).resolve().parents[2] / "pyproject.toml",
    )


def _string_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return ""


def _sequence_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list | tuple) and all(isinstance(item, str) for item in value):
        return ", ".join(value)
    return ""
