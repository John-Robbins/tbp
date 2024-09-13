"""Unit tests handling CTRL+C and CTRL+D in the Driver class."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

import signal
import time
from threading import Thread
from typing import TYPE_CHECKING, Any

from tbp.driver import Driver

if TYPE_CHECKING:
    from collections.abc import Generator

    import pytest
    from pytest import CaptureFixture  # noqa: PT013

empty_opts: Driver.Options = Driver.Options(nologo=True, file="", commands="")

###############################################################################
# What you are about to see in this file is a crime against Python, testing,
# and all programming best practices. Heed my advice! Don't do this at home. 😹
#
# When developing the CTRL+C and CTRL+D (CTRL+Z, ENTER on Windows) handling for
# tbp, I needed a way to do those keystrokes as they would occur with the
# Python built in input function. Traversing windswept mountain ranges of basic
# testing content and wading through the ancient swamps of outdated forum
# posts, I've found nothing that talks about how to test your app with those
# keystrokes under pytest.
#
# In tbp, there's hundreds of tests that use the very cool Monkey Patching to
# replace the built in Python input function. However, those tests, and any
# discussion of testing the input function, assume you're pumping in nice and
# normal text and not any interesting keystrokes. After much trial and error,
# I found a way to "pretend" CTRL+C and CTRL+D occur so my testing covers those
# cases.
#
# The key (HAH!) to CTRL+C and CTRL+D is that they generate exceptions,
# KeyboardInterrupt and EOFError, respectively. The question is how to get
# those generated in the proper context of the input function while testing.
# With the traditional Monkey Patching, you provide an iterator that loops
# through an array of text, which returns each line as though the user entered
# it in the input function.
#
# My idea was to build a generator, fake_input below, that takes a list of
# those strings, and when it sees special characters, it would raise the
# exception, just like occurs when using the input function. Turns out, that
# works! However, and this is super important, you must be sure your code
# handles the exception you raised and does not let it propagate out of your
# code. Also, because the generator called by pytest can get in a weird state
# when raising a KeyboardInterrupt for CTRL+C, always pass a default value to
# next. In my case, I use the tbp command language %q to quit.
#
# Like all hacks, I have no idea if this will keep working in the future.
#
# ELIT CAVE! - Developer beware!
###############################################################################


CTRL_C = "`"
CTRL_D = "^"


def fake_input(items: list[str]) -> Generator[str, Any, None]:
    """Fake input, but force exceptions to occur."""
    for i in items:
        if i == CTRL_C:
            raise KeyboardInterrupt
        if i == CTRL_D:
            raise EOFError
        yield i


def test_ctrl_d_from_debug_prompt(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CTRL+D from a breakpoint prompt."""
    cmds = [
        "10 LET C = 200",
        "20 LET H = 200",
        "700 END",
        "%bp 10",
        "RUN",
        CTRL_D,
        "%q",
    ]

    driver: Driver = Driver()
    # Create the generator.
    thing = fake_input(cmds)
    ret = 0
    monkeypatch.setattr("builtins.input", lambda _: next(thing, "%q"))
    ret = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 1
    assert "EOF interrupt: exiting tbp." in output.out


def test_ctrl_d_from_normal_prompt(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CTRL+D from a normal prompt."""
    cmds = [
        CTRL_D,
        "%q",
    ]

    driver: Driver = Driver()
    thing = fake_input(cmds)
    ret = 0
    monkeypatch.setattr("builtins.input", lambda _: next(thing, "%q"))
    ret = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 1
    assert "EOF interrupt: exiting tbp." in output.out


def test_ctrl_c_from_debug_prompt(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CTRL+C from a breakpoint prompt."""
    cmds = [
        "10 LET C = 200",
        "20 LET H = 200",
        "700 END",
        "%bp 10",
        "RUN",
        CTRL_C,
        "%q",
    ]

    driver: Driver = Driver()
    # Create the generator.
    thing = fake_input(cmds)
    monkeypatch.setattr("builtins.input", lambda _: next(thing, "%q"))
    ret = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "\n\n" in output.out


def test_ctrl_c_from_normal_prompt(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CTRL+C from a normal prompt."""
    cmds = [
        CTRL_C,
        "%q",
    ]

    driver: Driver = Driver()
    thing = fake_input(cmds)
    monkeypatch.setattr("builtins.input", lambda _: next(thing, "%q"))
    ret = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "\n\n" in output.out


def test_ctrl_c_from_running_code(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CTRL+C from a program."""
    cmds = [
        "10 INPUT A",
        "20 END",
        "RUN",
        CTRL_C,
        "%q",
    ]

    # Note that this works on the running state because the program is sitting
    # at 10 INPUT A, which gets the fake CTRL+C.
    driver: Driver = Driver()
    thing = fake_input(cmds)
    monkeypatch.setattr("builtins.input", lambda _: next(thing, "%q"))
    ret = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Keyboard Interrupt: Breaking out of program at line 10." in output.out


class AsyncControlC(Thread):
    """A class who's job is to signal CTRL+C."""

    def run(self: AsyncControlC) -> None:
        """Fakes a CTRL+C after a minor delay."""
        time.sleep(0.01)
        signal.raise_signal(signal.SIGINT)


def test_ctrl_c_from_program_load(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CTRL+C from loading a file."""
    cmds = [
        "%opt log t",
        '%lf "./examples/adventure.tbp"',
        "%opt log f",
        "%q",
    ]

    driver: Driver = Driver()
    thing = fake_input(cmds)
    ret = 0
    # In Python a CTRL+C signal is handled on the main thread, which is where
    # this method is running. I'll signal a CTRL+C from another thread so
    # control transfers back here where it will interrupt the large file
    # loading. I've also slowed down the loading by turning on logging.
    my_thread = AsyncControlC()
    my_thread.start()

    monkeypatch.setattr("builtins.input", lambda _: next(thing, "%q"))
    ret = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Aborting file loading" in output.out


def test_ctrl_c_saving_file(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CTRL+C when saving a file."""
    cmds = [
        "10 INPUT A",
        "20 END",
        '%sf "./examples/tbp.tbp"',
        CTRL_C,
        "%q",
    ]

    driver: Driver = Driver()
    thing = fake_input(cmds)
    monkeypatch.setattr("builtins.input", lambda _: next(thing, "%q"))
    ret = driver.party_like_it_is_1976(empty_opts)
    output = capsys.readouterr()
    assert ret == 0
    assert "Program not saved." in output.out
