"""The memory for the USR function."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2004 John Robbins
###############################################################################

from __future__ import annotations

from sortedcontainers import SortedDict


class Memory:
    """
    Implements the memory for reading and writing by the USR function.

    The "memory" is stored in a SortedDict, with the index being the 64 byte
    boundary.

    """

    # How the total memory size.
    TOTAL_MEM_SIZE = 65536

    BLOCK_SIZE = 64

    def __init__(self) -> None:
        """Initialize the Memory class."""
        self._memory: SortedDict[int, bytearray] = SortedDict()

    def write_memory(self, address: int, value: int) -> int:
        """Write a byte to memory."""
        if (block_index := address // self.BLOCK_SIZE) not in self._memory:
            self._memory[block_index] = bytearray(self.BLOCK_SIZE)

        self._memory[block_index][address - (block_index * self.BLOCK_SIZE)] = value

        return value

    def read_memory(self, address: int) -> int:
        """Read a byte from memory."""
        if (block_index := address // self.BLOCK_SIZE) not in self._memory:
            self._memory[block_index] = bytearray(self.BLOCK_SIZE)

        return self._memory[block_index][address - (block_index * self.BLOCK_SIZE)]
