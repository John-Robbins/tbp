"""Unit tests for the linter feature."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from typing import TYPE_CHECKING

from tbp.driver import Driver

if TYPE_CHECKING:
    import pytest
    from pytest import CaptureFixture  # noqa: PT013

empty_opts: Driver.Options = Driver.Options(nologo=True, file="", commands="")


def test_no_program_in_memory(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test no program to lint."""
    cmds = iter(
        [
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_no_end(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test program with no END."""
    cmds = iter(
        [
            "10 LET C = 200",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #01: Missing END statement in the program." in output.out


def test_end_in_program(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test program with END."""
    cmds = iter(
        [
            "10 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_clear_in_program(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test program with CLEAR."""
    cmds = iter(
        [
            "10 CLEAR",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #02: CLEAR must never be in a program." in output.out


def test_goto_in_program(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test program with good GOTO."""
    cmds = iter(
        [
            "10 GOTO 20",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_invalid_gosub_in_program(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test program with invalid GOSUB."""
    cmds = iter(
        [
            "10 GOSUB 200",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #03: GOSUB target not in program: '200'." in output.out


def test_good_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test good variable initialization."""
    cmds = iter(
        [
            "10 LET A=99",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_let_bad_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test uninitialized on 10 LET A=B."""
    cmds = iter(
        [
            "10 LET A=B",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'B'." in output.out


def test_let_bad_binary_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 10 LET A=10+C."""
    cmds = iter(
        [
            "10 LET A=10+C",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'C'." in output.out


def test_let_bad_unary_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 10 LET A=-D."""
    cmds = iter(
        [
            "10 LET A=-D",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'D'." in output.out


def test_let_bad_group_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 10 LET A=(E/10)+32."""
    cmds = iter(
        [
            "10 LET A=(E/10)+32",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'E'." in output.out


def test_let_bad_group_multiple_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 10 LET A=(E/10)+Q."""
    cmds = iter(
        [
            "10 LET A=(E/10)+Q",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'E'." in output.out
    assert "LINT #04: Potentially uninitialized variable 'Q'." in output.out


def test_input_good_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 10 INPUT A."""
    cmds = iter(
        [
            "10 INPUT A",
            "15 PR A",
            "20 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04" not in output.out


def test_if_good_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 IF A > B GOTO 50."""
    cmds = iter(
        [
            "10 A=1",
            "15 B=2",
            "30 IF A > B GOTO 50",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04" not in output.out


def test_if_bad_left_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 IF X > B GOTO 50."""
    cmds = iter(
        [
            "15 B=2",
            "30 IF X > B GOTO 50",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'X'." in output.out


def test_if_bad_right_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 IF B > Y GOTO 50."""
    cmds = iter(
        [
            "15 B=2",
            "30 IF B > Y GOTO 50",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'Y'." in output.out


def test_rnd_good_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=RND(B)."""
    cmds = iter(
        [
            "15 B=2",
            "30 LET A=RND(B)",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_rnd_bad_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=RND(K)."""
    cmds = iter(
        [
            "15 B=2",
            "30 LET A=RND(K)",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'K'." in output.out


def test_usr_good_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=USR(B)."""
    cmds = iter(
        [
            "15 B=276",
            "30 LET A=USR(B)",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_usr_good_x_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=USR(S+24,B)."""
    cmds = iter(
        [
            "15 B=276",
            "30 LET A=USR(S+24,B)",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_usr_good_x_a_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=USR(S+24,B,B)."""
    cmds = iter(
        [
            "15 B=276",
            "30 LET A=USR(S+24,B,B)",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT" not in output.out


def test_usr_bad_x_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=USR(S+24,B,B)."""
    cmds = iter(
        [
            "15 B=276",
            "30 LET A=USR(S+24,C,B)",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'C'." in output.out


def test_usr_bad_a_initialization(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=USR(S+24,B,B)."""
    cmds = iter(
        [
            "15 B=276",
            "30 LET A=USR(S+24,B,P)",
            "50 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'P'." in output.out


def test_init_later(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 30 LET A=USR(S+24,B,B)."""
    cmds = iter(
        [
            "15 PR B",
            "20 PR C",
            "30 GOTO 300",
            "100 LET B=1",
            "500 END",
            "%lint",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'C'." in output.out
    assert "LINT #03: GOTO target not in program: '300'." in output.out


def test_lint_strict(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test strict linting."""
    cmds = iter(
        [
            "15 LET A=A",
            "20 PR C",
            "100 LET C=1",
            "500 END",
            "%lint strict",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "LINT #04: Potentially uninitialized variable 'C'." in output.out
    assert "LINT #04: Potentially uninitialized variable 'A'." in output.out


def test_lint_strict_multiple_of_same(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test strict linting."""
    cmds = iter(
        [
            "15 LET B=C",
            "20 PR C",
            "100 LET A=C+C",
            "500 END",
            "%lint strict",
            "%q",
        ],
    )
    driver: Driver = Driver()
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    ret: int = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    msg = "LINT #04: Potentially uninitialized variable 'C'."
    assert msg in output.out
    assert output.out.count("LINT #04: Potentially uninitialized variable 'C'.") == 4
