"""Parser registry and command dispatch."""

from __future__ import annotations

import importlib
import inspect
import re
import warnings
from collections import OrderedDict
from dataclasses import dataclass
from functools import cached_property
from threading import RLock
from typing import Any, Callable, Literal

from yenie_parser.exceptions import (
    AmbiguousCommandError,
    ParserExecutionError,
    UnparsedOutputError,
    UnsupportedCommandError,
    UnsupportedPlatformError,
    YenieParserWarning,
)

ParserCallable = Callable[..., dict]
OnFailure = Literal["none", "empty_dict", "raw_output"]

_PLACEHOLDER_RE = re.compile(r"^\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\}$")
_QUOTED_PLACEHOLDER_RE = re.compile(r'^"\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\}"$')
_ON_FAILURE_VALUES = frozenset(("none", "empty_dict", "raw_output"))
_PSEUDO_LITERAL_PLACEHOLDERS = {"database", "default", "details", "ipv4", "ipv6"}
_TRAILING_SPACED_PLACEHOLDERS = {"interface", "interface_name", "intf_or_ip"}
_FIND_MATCHES_CACHE_MAXSIZE = 1024
_CACHE_LOCK = RLock()
_REGISTRY_CACHE: dict[str, tuple["ParserEntry", ...]] = {}
_FIND_MATCHES_CACHE: OrderedDict[tuple[str, str], tuple["CommandMatch", ...]] = OrderedDict()


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


def parse(
    *,
    platform: str,
    command: str,
    raw_output: str,
    strict: bool = False,
    warn: bool = False,
    on_failure: OnFailure = "none",
) -> dict[str, Any] | None | str:
    _validate_on_failure(on_failure)
    platform_key = normalize_platform(platform)
    if platform_key != "iosxe":
        return _handle_parse_failure(
            UnsupportedPlatformError(f"Unsupported platform: {platform!r}"),
            raw_output=raw_output,
            strict=strict,
            warn=warn,
            on_failure=on_failure,
        )

    matches = find_matches(platform_key, command)
    if not matches:
        return _handle_parse_failure(
            UnsupportedCommandError(f"Unsupported command for {platform_key}: {command!r}"),
            raw_output=raw_output,
            strict=strict,
            warn=warn,
            on_failure=on_failure,
        )

    best_score = matches[0].score
    best_matches = [match for match in matches if match.score == best_score]
    if len(best_matches) > 1 and len({match.entry.parser_class for match in best_matches}) > 1:
        templates = ", ".join(match.entry.template for match in best_matches)
        return _handle_parse_failure(
            AmbiguousCommandError(f"Ambiguous command {command!r}; matched: {templates}"),
            raw_output=raw_output,
            strict=strict,
            warn=warn,
            on_failure=on_failure,
        )

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
        return _handle_parse_failure(
            UnparsedOutputError(
                f"Parser produced no structured data for {platform_key} command {command!r}"
            ),
            raw_output=raw_output,
            strict=strict,
            warn=warn,
            on_failure=on_failure,
        )
    if first_error is not None:
        return _handle_parse_failure(
            ParserExecutionError(f"Parser execution failed for {platform_key} command {command!r}"),
            raw_output=raw_output,
            strict=strict,
            warn=warn,
            on_failure=on_failure,
            cause=first_error,
        )
    return _handle_parse_failure(
        UnsupportedCommandError(f"Unsupported command for {platform_key}: {command!r}"),
        raw_output=raw_output,
        strict=strict,
        warn=warn,
        on_failure=on_failure,
    )


def _validate_on_failure(on_failure: object) -> None:
    if not isinstance(on_failure, str) or on_failure not in _ON_FAILURE_VALUES:
        values = ", ".join(repr(value) for value in sorted(_ON_FAILURE_VALUES))
        raise ValueError(f"Invalid on_failure value {on_failure!r}; expected one of: {values}")


def _handle_parse_failure(
    error: Exception,
    *,
    raw_output: str,
    strict: bool,
    warn: bool,
    on_failure: OnFailure,
    cause: Exception | None = None,
) -> dict[str, Any] | None | str:
    if warn:
        warnings.warn(str(error), YenieParserWarning, stacklevel=2)
    if strict:
        if cause is not None:
            raise error from cause
        raise error
    return _on_failure_value(raw_output=raw_output, on_failure=on_failure)


def _on_failure_value(*, raw_output: str, on_failure: OnFailure) -> dict[str, Any] | None | str:
    if on_failure == "none":
        return None
    if on_failure == "empty_dict":
        return {}
    if on_failure == "raw_output":
        return raw_output
    raise AssertionError(f"Unhandled on_failure value: {on_failure!r}")


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
    platform_key = normalize_platform(platform)
    normalized_command = normalize_command(command)
    cache_key = (platform_key, normalized_command)

    with _CACHE_LOCK:
        if cache_key in _FIND_MATCHES_CACHE:
            cached_matches = _FIND_MATCHES_CACHE.pop(cache_key)
            _FIND_MATCHES_CACHE[cache_key] = cached_matches
            return list(_copy_matches(cached_matches))

    matches = [
        entry_match
        for entry in get_registry(platform_key)
        if (entry_match := entry.match(normalized_command))
    ]
    matches.sort(key=lambda match: match.score, reverse=True)
    cached_matches = _copy_matches(matches)

    with _CACHE_LOCK:
        _FIND_MATCHES_CACHE[cache_key] = cached_matches
        _FIND_MATCHES_CACHE.move_to_end(cache_key)
        while len(_FIND_MATCHES_CACHE) > _FIND_MATCHES_CACHE_MAXSIZE:
            _FIND_MATCHES_CACHE.popitem(last=False)

    return matches


def get_registry(platform: str) -> tuple[ParserEntry, ...]:
    platform_key = normalize_platform(platform)
    if platform_key != "iosxe":
        return ()
    with _CACHE_LOCK:
        if platform_key not in _REGISTRY_CACHE:
            _REGISTRY_CACHE[platform_key] = _load_iosxe_registry()
        return _REGISTRY_CACHE[platform_key]


def supported_commands(platform: str = "iosxe") -> tuple[str, ...]:
    return tuple(entry.template for entry in get_registry(platform))


def clear_caches() -> None:
    """Clear registry and command-match caches."""
    with _CACHE_LOCK:
        _REGISTRY_CACHE.clear()
        _FIND_MATCHES_CACHE.clear()


def _copy_matches(matches: tuple[CommandMatch, ...] | list[CommandMatch]) -> tuple[CommandMatch, ...]:
    return tuple(
        CommandMatch(
            entry=match.entry,
            kwargs=dict(match.kwargs),
            exact_template=match.exact_template,
            score=match.score,
        )
        for match in matches
    )


def _captures_trailing_text(tokens: tuple[str, ...], index: int) -> bool:
    if index != len(tokens) - 1:
        return False
    literal_tokens = {token.lower() for token in tokens}
    return "|" in literal_tokens and {"section", "count", "include"} & literal_tokens


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
        importlib.import_module("yenie_parser.iosxe._genie_show_interface"),
        importlib.import_module("yenie_parser.iosxe._genie_show_run"),
        importlib.import_module("yenie_parser.iosxe._genie_show_routing"),
        importlib.import_module("yenie_parser.iosxe._genie_show_aaa"),
        importlib.import_module("yenie_parser.iosxe._genie_show_cts"),
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
