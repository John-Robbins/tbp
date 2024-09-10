"""Unit tests for the Driver class."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from tbp.driver import Driver

if TYPE_CHECKING:
    from pathlib import Path

    import pytest
    from pytest import CaptureFixture  # noqa: PT013

empty_opts: Driver.Options = Driver.Options(nologo=True, file="", commands="")


def test_initialization() -> None:
    """Test to see if the Interpreter initializes."""
    driver: Driver = Driver()
    assert driver is not None


def test_empty_cmd_lang(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%'."""
    driver: Driver = Driver()
    input_data = StringIO("%")
    monkeypatch.setattr("sys.stdin", input_data)
    ret: int = driver.party_like_it_is_1976(empty_opts)
    assert ret == 0
    output = capsys.readouterr()
    assert "CLE #01: Invalid or unknown command : '%'" in output.out


def test_cmd_lang_quit(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%q'."""
    driver: Driver = Driver()
    input_data = StringIO("%q")
    monkeypatch.setattr("sys.stdin", input_data)
    ret: int = driver.party_like_it_is_1976(empty_opts)
    assert ret == 0
    output = capsys.readouterr()
    assert "Thank you for using tbp!" in output.out


def test_cmd_short_help(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%?^%q'."""
    commands = r"%?\n%q\n"
    driver: Driver = Driver()
    input_data = StringIO(commands)
    monkeypatch.setattr("sys.stdin", input_data)
    ret: int = driver.party_like_it_is_1976(empty_opts)
    assert ret == 0
    output = capsys.readouterr()
    assert "This help for the command language." in output.out


def test_cmd_long_help(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%help^%q'."""
    commands = r"%help\n%q\n"
    driver: Driver = Driver()
    input_data = StringIO(commands)
    monkeypatch.setattr("sys.stdin", input_data)
    ret: int = driver.party_like_it_is_1976(
        Driver.Options(nologo=False, file="", commands=""),
    )
    assert ret == 0
    output = capsys.readouterr()
    assert "This full help information." in output.out
    assert "Party like it's 1976!" in output.out


def test_cmd_log_alone(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt log'."""
    commands = r"%opt log\n"
    driver: Driver = Driver()
    input_data = StringIO(commands)
    monkeypatch.setattr("sys.stdin", input_data)
    ret: int = driver.party_like_it_is_1976(empty_opts)
    assert ret == 0
    output = capsys.readouterr()
    assert "Option: logging is False" in output.out


def test_cmd_log_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt log t^list'."""
    cmds = iter(["%opt log t", "%opt log", "list", "%opt log f", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    assert ret == 0
    # I'm just tired of it all. I've set pytest up exactly as the docs say
    # but there's no debug logging. I give up.
    # output = capsys.readouterr()
    # assert "[LIST (0,0)][CRLF (0,4)]" in output.out


def test_savefile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%savefile good file'."""
    program = '10 PR "Harold!"\n'
    temp_file = tmp_path / "good.tbp"
    cmds = iter([program, f'%savefile "{temp_file!s}"', "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    assert ret == 0
    assert temp_file.read_text() == program


def test_savefile_no_parm(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%savefile' no parameter."""
    cmds = iter(["%savefile", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert (
        "CLE #02: Missing required filename or missing quote delimiters "
        "for %savefile/%openfile." in output.out
    )


def test_savefile_no_program(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    """Test '%savefile good file' no program."""
    temp_file = tmp_path / "good.tbp"
    cmds = iter([f'%savefile "{temp_file!s}"', "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #03: No program in memory to save." in output.out


def test_opt_no_parm(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt' no parameter."""
    cmds = iter(["%opt", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #04: Required option is missing." in output.out


def test_opt_time_status(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt time'."""
    cmds = iter(["%opt time", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Option: time is False." in output.out


def test_opt_time_set_true(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt time t'."""
    cmds = iter(["%opt time t", "%opt time", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Option: time is True." in output.out


def test_opt_time_set_false(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt time False'."""
    cmds = iter(["%opt time t", "%opt time f", "%opt time", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Option: time is False." in output.out


def test_opt_run_load_status(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt run_on_load' no parameter."""
    cmds = iter(["%opt run_on_load", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Option: run_on_load is False." in output.out


def test_opt_run_load_set_true(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt run_on_load t'."""
    cmds = iter(["%opt run_on_load t", "%opt run_on_load", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Option: run_on_load is True." in output.out


def test_opt_run_load_set_false(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%opt run_on_load False."""
    cmds = iter(
        ["%opt run_on_load t", "%opt run_on_load False", "%opt run_on_load", "%q"],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Option: run_on_load is False." in output.out


def test_loadfile_no_parm(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%loadfile' no parameter."""
    cmds = iter(["%loadfile", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert (
        "CLE #02: Missing required filename or missing quote delimiters "
        "for %savefile/%loadfile." in output.out
    )


def test_loadfile(
    capsys: CaptureFixture[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test '%loadfile good file'."""
    program = """10 PRINT "Harold!"
20 PRINT "Scout!"
30 END
"""
    temp_file = tmp_path / "good.tbp"
    temp_file.write_text(program)
    cmds = iter([f'%loadfile "{temp_file!s}"', "LIST", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert program in output.out


def test_openfile_as_option(
    capsys: CaptureFixture[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'tbp file.tbp'."""
    program = """10 PRINT "Harold!"
20 PRINT "Scout!"
30 END
"""
    temp_file = tmp_path / "good.tbp"
    temp_file.write_text(program)
    cmds = iter(["LIST", "%q"])
    # fmt: off
    # I want the single quotes on file to drive code coverage. Love that Ruff
    # let's us disable formatting just for cases like this! 👍
    opts = Driver.Options(nologo=True, file=f'{temp_file!s}', commands="")  # noqa: Q000
    # fmt off
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(opts)
    output = capsys.readouterr()
    assert ret == 0
    assert program in output.out


def test_commands_as_option(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test `tbp -c stuff'."""
    cmds = iter(["%q"])
    opts = Driver.Options(nologo=True, file="", commands='A=420^PR "Var A=";A')
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Var A=420" in output.out


def test_commands_quit(
    capsys: CaptureFixture[str],
) -> None:
    """Test `tbp -c stuff'."""
    opts = Driver.Options(nologo=True, file="", commands="%q")
    driver: Driver = Driver()
    ret: int = driver.party_like_it_is_1976(opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Thank you for using tbp! Your patronage is appreciated." in output.out


def test_line_timer(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %opt time t."""
    cmds = iter(
        [
            "10 LET C = 200",
            "20 LET H = 200",
            "25 LET P = 0",
            "30 GOSUB 400",
            "40 GOTO 60",
            '50 PR "Never run, I hope!"',
            "60 IF C = 200 THEN GOSUB 400",
            "70 IF H = 200 IF C = 200 THEN GOSUB 400",
            "80 IF C = 2 GOTO 50",
            "90 IF C = 1 IF H = 3 GOTO 50",
            "100 GOSUB C+H",
            "130 IF C = 200 GOSUB H+C",
            '200 PR "I bid thee, adieu!"',
            "240 GOTO 700",
            "400 LET P=P+1",
            '420 PR "400 called ";P;" times"',
            "450 RETURN",
            "700 END",
            "%opt time t",
            "RUN",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "[130] = " in output.out


def test_run_from_breakpoint(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test RUN from breakpoint."""
    cmds = iter(
        [
            "10 LET C = 200",
            "20 LET H = 200",
            "700 END",
            "%bp 10",
            "RUN",
            "%v",
            "RUN",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #16: Use %c to continue from a breakpoint instead of RUN." in output.out
