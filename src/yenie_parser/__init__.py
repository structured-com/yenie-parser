"""Standalone Cisco CLI parsers."""

from importlib.metadata import version

from yenie_parser._registry import clear_caches, parse, supported_commands
from yenie_parser.exceptions import (
    AmbiguousCommandError,
    ParserExecutionError,
    UnparsedOutputError,
    YenieParserError,
    YenieParserWarning,
    UnsupportedCommandError,
    UnsupportedPlatformError,
)

__version__ = version("yenie-parser")

__all__ = [
    "AmbiguousCommandError",
    "ParserExecutionError",
    "UnparsedOutputError",
    "YenieParserError",
    "YenieParserWarning",
    "UnsupportedCommandError",
    "UnsupportedPlatformError",
    "__version__",
    "clear_caches",
    "parse",
    "supported_commands",
]
