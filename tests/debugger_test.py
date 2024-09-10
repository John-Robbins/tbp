"""Unit tests for the debugger."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from typing import TYPE_CHECKING

from tbp.driver import Driver

# I have no idea what the problem is, but 'import pytest' does not bring in the
# CaptureFixture type needed. Explicitly importing it, triggers the PT013 from
# Ruff. I give up.

# https://docs.astral.sh/ruff/rules/pytest-incorrect-pytest-import/
if TYPE_CHECKING:
    import pytest
    from pytest import CaptureFixture  # noqa: PT013

empty_opts: Driver.Options = Driver.Options(nologo=True, file="", commands="")


def test_variable_display(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %v command."""
    cmds = iter(["%vars", "%q"])
    driver: Driver = Driver()
    # Note that the lambda below gives Pylance problems. In VSCode project
    # settings I had to add the following to get rid of the errors as I could
    # not find a way to get the types set correctly.
    #    "python.analysis.diagnosticSeverityOverrides": {
    #    "reportUnknownArgumentType": "none",
    #    "reportUnknownLambdaType": "none"
    # }
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "S=256" in output.out


def test_no_breakpoints(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %bp command."""
    cmds = iter(["%bp", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "No breakpoints set." in output.out


def test_no_line_breakpoints(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %bp 10 command."""
    cmds = iter(["%bp 10", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #06: Line does not exist in the program: '10'." in output.out


def test_setting_breakpoints(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %bp 10 command on a valid line."""
    cmds = iter(['10 PR "Harold"', "%bp 10", "%bp", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Breakpoints set on:" in output.out


def test_setting_breakpoint_delete_line(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %bp 10 command and deleting the line."""
    cmds = iter(['10 PR "Harold"', "%bp 10", "10", "%bp", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "No breakpoints set." in output.out


def test_setting_breakpoint_invalid_param(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %bp * invalid command."""
    cmds = iter(["%bp *", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert (
        "CLE #05: %break and %delete commands require line numbers as parameters: '*'"
        in output.out
    )


def test_delete_all_breakpoints(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %d * command and deleting all breakpoints."""
    cmds = iter(['10 PR "Harold"', "%bp 10", "%d *", "%bp", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "No breakpoints set." in output.out


def test_delete_single_breakpoint(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %d 10 command with one breakpoint set."""
    cmds = iter(['10 PR "Harold"', "%bp 10", "%d 10", "%bp", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "No breakpoints set." in output.out


def test_delete_nonexistent_breakpoint(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %d 10 command with no breakpoint."""
    cmds = iter(["%d 10", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #06: Line does not exist in the program: '10'." in output.out


def test_delete_breakpoint_invalid_param(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %bp * invalid command."""
    cmds = iter(['%bp "*"', "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert (
        "CLE #05: %break and %delete commands require line numbers as parameters:"
        in output.out
    )


def test_multiple_breakpoint_on_line(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the %bp 10 %bp 10."""
    cmds = iter(['10 PR "Harold"', "%bp 10", "%bp 10", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #14: Breakpoint already set on '10'." in output.out


def test_not_debugging_commands(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the all the debugger commands fail when not debugging."""
    cmds = iter(["%c", "%s", "%bt", "%e", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #08: %continue" in output.out
    assert "CLE #08: %step" in output.out
    assert "CLE #08: %backtrace" in output.out
    assert "CLE #08: %exit" in output.out


def test_simple_breakpoint_commands(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test a simple breakpoint."""
    cmds = iter(['10 PR "Harold"', "20 END", "%bp 10", "run", "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert '[10 PR "Harold"]' in output.out


def test_stack(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %bt command."""
    cmds = iter(
        [
            "10 GOSUB 40",
            "20 END",
            '40 PR "Scout"',
            "50 RETURN",
            "%bp 40",
            "run",
            "%bt",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "-- Call Stack --\n20 END" in output.out


def test_step(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %s command."""
    cmds = iter(
        [
            "10 GOSUB 40",
            "20 END",
            '40 PR "Scout"',
            "50 RETURN",
            "%bp 40",
            "RUN",
            "%s",
            "%s",
            "%s",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert '[40 PR "Scout"]' in output.out
    assert "[50 RETURN]" in output.out
    assert "[20 END]" in output.out


def test_step_on_goto(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %s with GOTO command."""
    cmds = iter(
        [
            "10 GOSUB 40",
            "20 END",
            '40 PR "Scout"',
            "50 RETURN",
            "%bp 10",
            "RUN",
            "%s",
            "%s",
            "%s",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "[10 GOSUB 40]" in output.out
    assert "[20 END]" in output.out


def test_step_if_command(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %s with IF command."""
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
            "%bp 70",
            "RUN",
            "%s",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "[400 LET P=P+1]" in output.out


def test_debugging_delete_line(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %s command."""
    cmds = iter(
        [
            "10 GOSUB 40",
            "20 END",
            '40 PR "Scout"',
            "50 RETURN",
            "%bp 10",
            "RUN",
            "20",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #09: Deleting program lines while debugging disabled." in output.out


def test_debugging_invalid_branch(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %s command."""
    cmds = iter(
        [
            "10 GOSUB 4000",
            "20 END",
            '40 PR "Scout"',
            "50 RETURN",
            "%bp 10",
            "RUN",
            "%s",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #10: Branch target does not exist '4000'." in output.out


def test_debugging_invalid_return(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %s command."""
    cmds = iter(
        [
            "10 RETURN",
            "20 END",
            "%bp 10",
            "RUN",
            "%s",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #11: RETURN call stack is empty." in output.out


def test_open_file_while_debugging(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %lf while debugging."""
    cmds = iter(['10 PR "Harold"', "20 END", "%bp 10", "run", '%lf "fake.tbp"', "%q"])
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #15: %loadfile disabled while debugging." in output.out


def test_debugging_exit(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %exit command."""
    cmds = iter(
        [
            "10 GOSUB 40",
            "20 END",
            '40 PR "Scout"',
            "50 RETURN",
            "%bp 10",
            "RUN",
            "%exit",
            "%continue",
            "%quit",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "CLE #08: %continue" in output.out


def test_debugging_invalid_bp_delete(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test %d <invalid> command."""
    cmds = iter(
        [
            "10 GOSUB 40",
            "20 END",
            '40 PR "Scout"',
            "50 RETURN",
            "%bp 10",
            "%d log",
            "%exit",
            "%continue",
            "%quit",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert (
        "CLE #05: %break and %delete commands require line numbers as parameters:"
        in output.out
    )
