"""Small local shims for Genie parser code adapted into Yenie Parser."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any as TypingAny


class MetaParser:
    """Compatibility base for adapted Genie parser classes."""


@dataclass(frozen=True)
class _SchemaToken:
    name: str
    args: tuple[TypingAny, ...]

    def __repr__(self) -> str:
        args = ", ".join(repr(arg) for arg in self.args)
        return f"{self.name}({args})"


def _schema_token(name: str, *args: TypingAny) -> _SchemaToken:
    return _SchemaToken(name, args)


def Any(*args: TypingAny) -> _SchemaToken:  # noqa: N802
    return _schema_token("Any", *args)


def Optional(*args: TypingAny) -> _SchemaToken:  # noqa: N802
    return _schema_token("Optional", *args)


def Or(*args: TypingAny) -> _SchemaToken:  # noqa: N802
    return _schema_token("Or", *args)


def And(*args: TypingAny) -> _SchemaToken:  # noqa: N802
    return _schema_token("And", *args)


def Default(*args: TypingAny) -> _SchemaToken:  # noqa: N802
    return _schema_token("Default", *args)


def Use(*args: TypingAny) -> _SchemaToken:  # noqa: N802
    return _schema_token("Use", *args)


def ListOf(value: TypingAny) -> list[TypingAny]:  # noqa: N802
    return [value]


class Schema:
    """Compatibility wrapper for schema declarations."""

    def __init__(self, schema: TypingAny) -> None:
        self.schema = schema


@dataclass(frozen=True)
class _TabularResult:
    entries: dict[TypingAny, dict[str, TypingAny]]


def oper_fill_tabular(  # noqa: N802
    *,
    header_fields: list[str],
    label_fields: list[str],
    device_output: str,
    device_os: str | None = None,
    index: list[int] | None = None,
    **kwargs: TypingAny,
) -> _TabularResult:
    """Small parsergen.oper_fill_tabular replacement for adapted Genie parsers."""

    del device_os, kwargs
    entries: dict[TypingAny, dict[str, TypingAny]] = {}
    index_columns = index or [0]
    parsing_rows = False

    for raw_line in device_output.splitlines():
        line = raw_line.strip()
        if not line or set(line) <= {"-"}:
            continue
        if all(field in line for field in header_fields):
            parsing_rows = True
            continue
        if not parsing_rows:
            continue

        columns = line.split()
        if len(columns) < len(label_fields):
            continue
        if len(columns) > len(label_fields):
            columns = columns[: len(label_fields) - 1] + [" ".join(columns[len(label_fields) - 1 :])]

        row = dict(zip(label_fields, columns, strict=True))
        key_parts = tuple(columns[column] for column in index_columns)
        key: TypingAny = key_parts[0] if len(key_parts) == 1 else key_parts
        entries[key] = row

    return _TabularResult(entries=entries)


class Common:
    """Subset of Genie common helpers needed by adapted parsers."""

    _INTERFACE_PREFIXES = (
        ("TwoGigabitEthernet", "TwoGigabitEthernet"),
        ("TwentyFiveGigE", "TwentyFiveGigE"),
        ("TenGigabitEthernet", "TenGigabitEthernet"),
        ("FortyGigabitEthernet", "FortyGigabitEthernet"),
        ("FiveGigabitEthernet", "FiveGigabitEthernet"),
        ("HundredGigE", "HundredGigE"),
        ("GigabitEthernet", "GigabitEthernet"),
        ("FastEthernet", "FastEthernet"),
        ("Ethernet", "Ethernet"),
        ("Serial", "Serial"),
        ("Port-channel", "Port-channel"),
        ("Loopback", "Loopback"),
        ("Vlan", "Vlan"),
        ("Twe", "TwentyFiveGigE"),
        ("Two", "TwoGigabitEthernet"),
        ("Ten", "TenGigabitEthernet"),
        ("Te", "TenGigabitEthernet"),
        ("Fo", "FortyGigabitEthernet"),
        ("Fi", "FiveGigabitEthernet"),
        ("Hu", "HundredGigE"),
        ("Gig", "GigabitEthernet"),
        ("Gi", "GigabitEthernet"),
        ("Fas", "FastEthernet"),
        ("Fa", "FastEthernet"),
        ("Eth", "Ethernet"),
        ("Et", "Ethernet"),
        ("Ser", "Serial"),
        ("Po", "Port-channel"),
        ("Lo", "Loopback"),
        ("Vl", "Vlan"),
    )

    @classmethod
    def convert_intf_name(cls, interface: str | None = None, **kwargs: TypingAny) -> str:
        if interface is None:
            interface = kwargs.get("intf", "")
        stripped = interface.strip()
        for short, long in cls._INTERFACE_PREFIXES:
            if stripped.lower().startswith(short.lower()):
                suffix = stripped[len(short) :]
                suffix = suffix.lstrip() if suffix[:1].isspace() else suffix
                if suffix and (suffix[0].isdigit() or suffix[0] in "./"):
                    return f"{long}{suffix}"
                if stripped.lower() == short.lower():
                    return long
        return stripped
