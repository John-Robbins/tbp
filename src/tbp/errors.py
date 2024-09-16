"""The tpb exception types."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations


class TbpBaseError(Exception):
    """The base exception class for a tbp exceptions."""

    def __init__(self: TbpBaseError, line: int, column: int, message: str) -> None:
        """Initialize the base class."""
        self.line = line
        self.column = column
        self.message = message
        self.friendly_name = "!!!BASE EXCEPTION CLASS!!!"

    def __str__(self: TbpBaseError) -> str:
        """Nicely prints the exception."""
        # This is a neat trick I learned from Ruff. Instead of splitting
        # f-strings across lines with `\`, put the whole string in parenthesis,
        # like shown below.
        return (
            f"{self.friendly_name}: [Ln {self.line}, "
            f"Col {self.column}] ({self.message})"
        )


class TbpSyntaxError(TbpBaseError):
    """The error thrown while scanning and basic parsing."""

    def __init__(self: TbpSyntaxError, line: int, column: int, message: str) -> None:
        """Initialize the syntax error exception."""
        super().__init__(line, column, message)
        self.friendly_name = "Syntax Error"


class TbpRuntimeError(TbpBaseError):
    """The error thrown while executing."""

    def __init__(self: TbpRuntimeError, line: int, column: int, message: str) -> None:
        """Initialize the runtime error exception."""
        super().__init__(line, column, message)
        self.friendly_name = "Runtime Error"
