"""The symbol table for Tiny BASIC in Python."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

# Note that Sorted Containers does not have any typing information in the code.
# Make sure to install the sortedcontainers-stubs package for full support.
# https://github.com/h4l/sortedcontainers-stubs
from sortedcontainers import SortedDict

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class SymbolInfo:
    """
    The state of a variable.

    This class is returned by the SymbolTable class when a variable is requested.
    """

    # True indicates the variable is properly initialized. If False, the value
    # field can be anything.
    initialized: bool
    value: int


@dataclass
class SymbolTable:
    """The symbol table/environment for Tiny BASIC."""

    # What we use to store our 26 variables. I wanted them sorted so I'll use
    # the fast and scalable Sorted Collections.
    # Pylint and Ruff doesn't like the lambda here, but mypy complains without
    # it.
    _variables: SortedDict[str, SymbolInfo] = field(
        default_factory=lambda: SortedDict(),  # pylint: disable=unnecessary-lambda  # noqa: PLW0108
    )

    # The default value for uninitialized variables.
    default_uninitialized_value: int = 57005

    def __setitem__(self: SymbolTable, key: str, value: int) -> None:
        """Add or update a variable value."""
        self._variables[key] = SymbolInfo(initialized=True, value=value)

    def __getitem__(self: SymbolTable, key: str) -> SymbolInfo:
        """Return the data for the key."""
        if key in self._variables:
            return self._variables[key]
        return SymbolInfo(initialized=False, value=self.default_uninitialized_value)

    def __iter__(self: SymbolTable) -> Generator[tuple[str, SymbolInfo], Any, None]:
        """Enumerate the variables and return the tuple of the key and it's value."""
        for key in self._variables:
            yield key, self._variables[key]

    def values_string(self: SymbolTable) -> str:
        """Build a string of the initialized variables."""
        return_string: str = ""

        for index, (k, v) in enumerate(self._variables.items()):
            return_string += f"{k}={v.value:<10}"
            if (index + 1) % 6 == 0:
                return_string += "\n"

        # If there's not a CR/LF on the end of the string, add it.
        if len(return_string) > 1 and return_string[len(return_string) - 1] != "\n":
            return_string += "\n"

        return return_string
