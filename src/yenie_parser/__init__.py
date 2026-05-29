"""Standalone Cisco CLI parsers."""

from importlib.metadata import version

from yenie_parser._registry import parse, supported_commands
from yenie_parser.exceptions import (
    AmbiguousCommandError,
    YenieParserError,
    UnsupportedCommandError,
    UnsupportedPlatformError,
)

__version__ = version("yenie-parser")

__all__ = [
    "AmbiguousCommandError",
    "YenieParserError",
    "UnsupportedCommandError",
    "UnsupportedPlatformError",
    "__version__",
    "parse",
    "supported_commands",
]
