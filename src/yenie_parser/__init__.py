"""Standalone Cisco CLI parsers."""

from yenie_parser._registry import parse, supported_commands
from yenie_parser.exceptions import (
    AmbiguousCommandError,
    YenieParserError,
    UnsupportedCommandError,
    UnsupportedPlatformError,
)

__version__ = "0.2.0"

__all__ = [
    "AmbiguousCommandError",
    "YenieParserError",
    "UnsupportedCommandError",
    "UnsupportedPlatformError",
    "__version__",
    "parse",
    "supported_commands",
]
