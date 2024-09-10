"""Unit tests for the Language classes."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from tbp.languageitems import Literal, Variable


def test_initialization() -> None:
    """Test to see if the Interpreter initializes."""
    item: Literal = Literal(0, 0, 1)
    item.value = 0x111FFFF
    assert item.value == -1


def test_ctor() -> None:
    """Test to see if the Interpreter initializes."""
    item: Variable = Variable(0, 0, "A")
    item.value = 0xFFFF
    assert item.value == -1
