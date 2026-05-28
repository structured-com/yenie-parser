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


class Common:
    """Subset of Genie common helpers needed by adapted parsers."""

    _INTERFACE_PREFIXES = (
        ("TwoGigabitEthernet", "TwoGigabitEthernet"),
        ("TwentyFiveGigE", "TwentyFiveGigE"),
        ("TenGigabitEthernet", "TenGigabitEthernet"),
        ("FortyGigabitEthernet", "FortyGigabitEthernet"),
        ("HundredGigE", "HundredGigE"),
        ("GigabitEthernet", "GigabitEthernet"),
        ("FastEthernet", "FastEthernet"),
        ("Ethernet", "Ethernet"),
        ("Port-channel", "Port-channel"),
        ("Loopback", "Loopback"),
        ("Vlan", "Vlan"),
        ("Twe", "TwentyFiveGigE"),
        ("Two", "TwoGigabitEthernet"),
        ("Te", "TenGigabitEthernet"),
        ("Fo", "FortyGigabitEthernet"),
        ("Hu", "HundredGigE"),
        ("Gi", "GigabitEthernet"),
        ("Fa", "FastEthernet"),
        ("Eth", "Ethernet"),
        ("Et", "Ethernet"),
        ("Po", "Port-channel"),
        ("Lo", "Loopback"),
        ("Vl", "Vlan"),
    )

    @classmethod
    def convert_intf_name(cls, interface: str) -> str:
        stripped = interface.strip()
        for short, long in cls._INTERFACE_PREFIXES:
            if stripped.lower().startswith(short.lower()):
                suffix = stripped[len(short) :]
                if suffix and (suffix[0].isdigit() or suffix[0] in "./"):
                    return f"{long}{suffix}"
                if stripped.lower() == short.lower():
                    return long
        return stripped
