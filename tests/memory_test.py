"""Unit tests for the linter feature."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2004 John Robbins
###############################################################################

from __future__ import annotations

from tbp.memory import Memory

START_ADDRESS = 100


def test_memory() -> None:
    """Basic memory read and write across boundaries."""
    mem: Memory = Memory()
    for i in range(255):
        ret: int = mem.write_memory(START_ADDRESS + i, i)
        assert i == ret

    for i in range(255):
        ret2: int = mem.read_memory(START_ADDRESS + i)
        assert i == ret2
