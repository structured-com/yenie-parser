"""Parser registry and command dispatch."""

from __future__ import annotations

import importlib
import inspect
import re
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable

from yenie_parser.exceptions import (
    AmbiguousCommandError,
    UnsupportedCommandError,
    UnsupportedPlatformError,
)

ParserCallable = Callable[..., dict]

_PLACEHOLDER_RE = re.compile(r"^\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\}$")
_QUOTED_PLACEHOLDER_RE = re.compile(r'^"\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\}"$')
_PSEUDO_LITERAL_PLACEHOLDERS = {"database", "details", "policy"}
_TRAILING_SPACED_PLACEHOLDERS = {"interface", "interface_name", "intf_or_ip"}


@dataclass(frozen=True)
class ParserEntry:
    platform: str
    template: str
    parser_class: type
    source_order: int

    @cached_property
    def normalized_template(self) -> str:
        return normalize_command(self.template)

    @cached_property
    def placeholder_names(self) -> tuple[str, ...]:
        return tuple(name for token in self._tokens if (name := _placeholder_name(token)))

    @cached_property
    def literal_count(self) -> int:
        return sum(1 for token in self._tokens if not _placeholder_name(token))

    @cached_property
    def _tokens(self) -> tuple[str, ...]:
        return tuple(self.template.split())

    @cached_property
    def _pattern(self) -> re.Pattern[str]:
        pieces = []
        tokens = self._tokens
        for index, token in enumerate(tokens):
            name = _placeholder_name(token)
            if name:
                if name in _PSEUDO_LITERAL_PLACEHOLDERS:
                    pieces.append(fr"(?P<{name}>\{{{name}\}}|{re.escape(name)})")
                elif _QUOTED_PLACEHOLDER_RE.match(token):
                    pieces.append(fr'"(?P<{name}>[^"]+)"')
                elif _captures_trailing_text(tokens, index) or _captures_trailing_spaced_value(
                    name, tokens, index
                ):
                    pieces.append(fr"(?P<{name}>.+)")
                else:
                    pieces.append(fr"(?P<{name}>\S+)")
            else:
                pieces.append(re.escape(token))
        return re.compile(r"^" + r"\s+".join(pieces) + r"$", re.IGNORECASE)

    def match(self, command: str) -> CommandMatch | None:
        normalized_command = normalize_command(command)
        regex_match = self._pattern.match(normalized_command)
        if not regex_match:
            return None
        exact = normalized_command.casefold() == self.normalized_template.casefold()
        return CommandMatch(
            entry=self,
            kwargs=regex_match.groupdict(),
            exact_template=exact,
            score=(int(exact), self.literal_count, len(self._tokens), self.source_order),
        )

    def parse(self, raw_output: str, kwargs: dict[str, str]) -> dict:
        parser = self.parser_class()
        cli = parser.cli
        accepted = set(inspect.signature(cli).parameters)
        call_kwargs = {key: value for key, value in kwargs.items() if key in accepted}
        call_kwargs["output"] = raw_output
        return cli(**call_kwargs)


@dataclass(frozen=True)
class CommandMatch:
    entry: ParserEntry
    kwargs: dict[str, str]
    exact_template: bool
    score: tuple[int, int, int, int]


def parse(*, platform: str, command: str, raw_output: str) -> dict:
    platform_key = normalize_platform(platform)
    if platform_key != "iosxe":
        raise UnsupportedPlatformError(f"Unsupported platform: {platform!r}")

    matches = find_matches(platform_key, command)
    if not matches:
        raise UnsupportedCommandError(f"Unsupported command for {platform_key}: {command!r}")

    best_score = matches[0].score
    best_matches = [match for match in matches if match.score == best_score]
    if len(best_matches) > 1 and len({match.entry.parser_class for match in best_matches}) > 1:
        templates = ", ".join(match.entry.template for match in best_matches)
        raise AmbiguousCommandError(f"Ambiguous command {command!r}; matched: {templates}")

    first_result: dict[str, Any] | None = None
    first_error: Exception | None = None
    for match in matches:
        try:
            result = match.entry.parse(raw_output, match.kwargs)
        except Exception as exc:  # pragma: no cover - defensive fallback for overlapping templates
            if first_error is None:
                first_error = exc
            continue
        if first_result is None:
            first_result = result
        if result:
            return result

    if first_result is not None:
        return first_result
    if first_error is not None:
        raise first_error
    return {}


def normalize_platform(platform: str) -> str:
    return platform.strip().lower()


def normalize_command(command: str) -> str:
    return " ".join(command.strip().split())


def _placeholder_name(token: str) -> str | None:
    for regex in (_PLACEHOLDER_RE, _QUOTED_PLACEHOLDER_RE):
        if match := regex.match(token):
            return match.group("name")
    return None


def find_matches(platform: str, command: str) -> list[CommandMatch]:
    matches = [entry_match for entry in get_registry(platform) if (entry_match := entry.match(command))]
    matches.sort(key=lambda match: match.score, reverse=True)
    return matches


def get_registry(platform: str) -> tuple[ParserEntry, ...]:
    platform_key = normalize_platform(platform)
    if platform_key != "iosxe":
        return ()
    return _load_iosxe_registry()


def supported_commands(platform: str = "iosxe") -> tuple[str, ...]:
    return tuple(entry.template for entry in get_registry(platform))


def _captures_trailing_text(tokens: tuple[str, ...], index: int) -> bool:
    if index != len(tokens) - 1:
        return False
    literal_tokens = {token.lower() for token in tokens}
    return "|" in literal_tokens and {"section", "count"} & literal_tokens


def _captures_trailing_spaced_value(name: str, tokens: tuple[str, ...], index: int) -> bool:
    return index == len(tokens) - 1 and name in _TRAILING_SPACED_PLACEHOLDERS


def _load_iosxe_registry() -> tuple[ParserEntry, ...]:
    modules = (
        importlib.import_module("yenie_parser.iosxe._genie_show_device_tracking"),
        importlib.import_module("yenie_parser.iosxe._genie_show_authentication_sessions"),
        importlib.import_module("yenie_parser.iosxe._genie_show_inventory"),
        importlib.import_module("yenie_parser.iosxe._genie_show_cdp"),
        importlib.import_module("yenie_parser.iosxe._genie_show_arp"),
        importlib.import_module("yenie_parser.iosxe._genie_show_fdb"),
    )
    entries: list[ParserEntry] = []
    for module in modules:
        for _, parser_class in inspect.getmembers(module, inspect.isclass):
            if parser_class.__module__ != module.__name__ or not hasattr(parser_class, "cli_command"):
                continue
            source_order = inspect.getsourcelines(parser_class)[1]
            commands = getattr(parser_class, "cli_command")
            if isinstance(commands, str):
                commands = [commands]
            for template in commands:
                entries.append(
                    ParserEntry(
                        platform="iosxe",
                        template=template,
                        parser_class=parser_class,
                        source_order=source_order,
                    )
                )

    entries.sort(key=lambda entry: (entry.source_order, entry.template))
    return tuple(entries)
