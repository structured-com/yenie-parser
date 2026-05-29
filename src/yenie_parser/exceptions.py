"""Public exceptions raised by Yenie Parser."""


class YenieParserError(Exception):
    """Base class for Yenie Parser exceptions."""


class YenieParserWarning(Warning):
    """Warning emitted when parsing fails in warning mode."""


class UnsupportedPlatformError(YenieParserError):
    """Raised when no parser registry exists for a platform."""


class UnsupportedCommandError(YenieParserError):
    """Raised when a command is not registered for the requested platform."""


class AmbiguousCommandError(YenieParserError):
    """Raised when command dispatch cannot choose a parser deterministically."""


class UnparsedOutputError(YenieParserError):
    """Raised when a matched parser produces no structured data."""


class ParserExecutionError(YenieParserError):
    """Raised when matched parsers fail during execution."""
