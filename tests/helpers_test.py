"""Unit tests for the helper functions."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from tbp.helpers import limit_input, load_program, save_program

if TYPE_CHECKING:
    from pathlib import Path

    import pytest
    from pytest import CaptureFixture  # noqa: PT013


def test_limit_invalid_param() -> None:
    """Test invalid valid_input list."""
    empty: list[str] = []
    flag, result = limit_input("Nope!", empty)
    assert flag is False
    assert not result


def test_limit_simple(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do a normal CR acceptance."""
    input_data = StringIO("\n")
    monkeypatch.setattr("sys.stdin", input_data)
    yes_no: list[str] = ["y", "n"]
    flag, result = limit_input("(Y/n)>", yes_no)
    assert flag is True
    assert result == "y"


def test_limit_second_option(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do a normal CR acceptance."""
    input_data = StringIO("n\n")
    monkeypatch.setattr("sys.stdin", input_data)
    yes_no: list[str] = ["y", "n"]
    flag, result = limit_input("(Y/n)>", yes_no)
    assert flag is True
    assert result == "n"


def test_limit_invalid_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do a normal CR acceptance."""
    cmds = iter(["p", "y"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    yes_no: list[str] = ["y", "n"]
    flag, result = limit_input("(Y/n)>", yes_no)
    output = capsys.readouterr()
    assert flag is True
    assert result == "y"
    assert "Invalid input." in output.out


def test_saving_new_file(tmp_path: Path) -> None:
    """Test saving a new file."""
    temp_file = tmp_path / "good.tbp"
    program = """
10 PRINT "Sammy!"
20 END
"""
    result = save_program(str(temp_file), program)
    assert result is True
    assert temp_file.read_text() == program


def test_overwriting_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Test overwriting an existing file."""
    temp_file = tmp_path / "overwrite.tbp"
    program = """
10 PRINT "Charlie!"
20 END
"""
    temp_file.write_text("some stuff....")
    input_data = StringIO("\n")
    monkeypatch.setattr("sys.stdin", input_data)
    result = save_program(str(temp_file), program)
    output = capsys.readouterr()
    assert result is True
    assert temp_file.read_text() == program
    assert "Do you want to overwrite the file? (Y/n)>" in output.out


def test_not_overwriting_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Test not overwriting an existing file."""
    temp_file = tmp_path / "overwrite.tbp"
    program = """
10 PRINT "Charlie!"
20 END
"""
    temp_file.write_text("some stuff....")
    input_data = StringIO("n\n")
    monkeypatch.setattr("sys.stdin", input_data)
    result = save_program(str(temp_file), program)
    output = capsys.readouterr()
    assert result is False
    assert "Do you want to overwrite the file? (Y/n)>" in output.out


def test_invalid_save_file(
    capsys: CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Test Saving to invalid filename."""
    temp_file = tmp_path / "\\/overwrite.tbp"
    program = """
10 PRINT "Charlie!"
20 END
"""
    result = save_program(str(temp_file), program)
    output = capsys.readouterr()
    assert result is False
    assert "CLE #12: Filename is invalid " in output.out


def test_loading_file(
    tmp_path: Path,
) -> None:
    """Test reading an existing file."""
    temp_file = tmp_path / "read.tbp"
    program = """
10 PRINT "Scout!"
20 END
"""
    temp_file.write_text(program)
    result = load_program(str(temp_file))
    assert isinstance(result, str)
    assert result == program


def test_try_loading_nonexistent(
    capsys: CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Test reading a file that doesn't exist."""
    temp_file = tmp_path / "read.tbp"
    result = load_program(str(temp_file))
    output = capsys.readouterr()
    assert not result
    assert "CLE #13: File does not exist" in output.out


def test_invalid_load_file(
    capsys: CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """Test loading an invalid filename."""
    temp_file = tmp_path / "\\/ick.tbp"
    result = load_program(str(temp_file))
    output = capsys.readouterr()
    assert not result
    assert "CLE #13: File does not exist" in output.out
