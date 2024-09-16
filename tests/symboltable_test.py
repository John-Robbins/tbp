"""Unit tests for the SymbolTable class."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from tbp.symboltable import SymbolTable


def test_initialization() -> None:
    """Test to see if the symbol table initializes."""
    table: SymbolTable = SymbolTable()
    assert table is not None


def test_adding() -> None:
    """Test to add a single item."""
    table: SymbolTable = SymbolTable()
    table["A"] = 1
    assert table["A"].initialized is True
    assert table["A"].value == 1


def test_not_added() -> None:
    """Test get a value that does not exist."""
    table: SymbolTable = SymbolTable()
    assert table["B"].initialized is False
    assert table["B"].value == table.default_uninitialized_value


def test_iteration() -> None:
    """Test iterating the symbol table."""
    table: SymbolTable = SymbolTable()
    for i in range(25):
        table[chr(ord("A") + i)] = i
    for k, item in table:
        assert table[k].value != table.default_uninitialized_value
        assert item.initialized is True


def test_values_uninitialized() -> None:
    """An uninitialized symbol table."""
    table: SymbolTable = SymbolTable()
    res: str = table.values_string()
    assert len(res) == 0


def test_values_display() -> None:
    """Test the display string."""
    table: SymbolTable = SymbolTable()
    for i in range(6):
        table[chr(ord("A") + i)] = i
    res: str = table.values_string()
    assert (
        res
        == "A=0         B=1         C=2         D=3         E=4         F=5         \n"
    )


def test_values_display_large_nums() -> None:
    """Test the display string with large numbers."""
    table: SymbolTable = SymbolTable()
    for i in range(4):
        table[chr(ord("A") + i)] = -32768
    res: str = table.values_string()
    assert res == "A=-32768    B=-32768    C=-32768    D=-32768    \n"


def test_values_display_full_monty() -> None:
    """Test the display string with all variables."""
    table: SymbolTable = SymbolTable()
    for i in range(26):
        table[chr(ord("A") + i)] = i * 100
    res: str = table.values_string()
    assert (
        res
        == "A=0         B=100       C=200       D=300       E=400       F=500       \n"
        "G=600       H=700       I=800       J=900       K=1000      L=1100      \n"
        "M=1200      N=1300      O=1400      P=1500      Q=1600      R=1700      \n"
        "S=1800      T=1900      U=2000      V=2100      W=2200      X=2300      \n"
        "Y=2400      Z=2500      \n"
    )
