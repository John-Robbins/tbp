"""Unit tests for the Command Language regular expression."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

import re

_CMD_GROUP: str = "cmd"
_PARAM_GROUP: str = "param"
_OPT_GROUP: str = "optval"

_CMD_REGEX_STRING = r"""
%(?P<cmd>
   help         |  \?      |
   quit         |  \bq\b   |
   loadfile     |  \blf\b  |
   opt          |
   break        |  \bbp\b  |
   backtrace    |  \bbt\b  |
   continue     |  \bc\b   |
   delete       |  \bd\b   |
   lint         |
   savefile     |  \bsf\b  |
   step         |  \bs\b   |
   vars         |  \bv\b   |
   exit         |  \be\b
 )
\s*
(?P<param>
   log          |
   time         |
   run_on_load  |
   strict       |
   \".*\"       |
   [*]          |
   [0-9]*       |
  )?
\s*
(?P<optval>
   true         | \bt\b |
   false        | \bf\b
 )?
	"""


_CMD_REGEX = re.compile(_CMD_REGEX_STRING, re.IGNORECASE | re.VERBOSE)


def test_help() -> None:
    """Test '%help'."""
    m = _CMD_REGEX.match("%help")
    assert m is not None
    assert m.group(_CMD_GROUP) == "help"
    m = _CMD_REGEX.match("%?")
    assert m is not None
    assert m.group(_CMD_GROUP) == "?"
    m = _CMD_REGEX.match("%hep")
    assert m is None


def test_quit() -> None:
    """Test '%quit'."""
    m = _CMD_REGEX.match("%quit")
    assert m is not None
    assert m.group(_CMD_GROUP) == "quit"
    m = _CMD_REGEX.match("%q")
    assert m is not None
    assert m.group(_CMD_GROUP) == "q"
    m = _CMD_REGEX.match("%qui")
    assert m is None


def test_loadfile() -> None:
    """Test '%openfile'."""
    m = _CMD_REGEX.match('%loadfile "somefile"')
    assert m is not None
    assert m.group(_CMD_GROUP) == "loadfile"
    assert m.group(_PARAM_GROUP) == '"somefile"'
    m = _CMD_REGEX.match('%lf "blah"')
    assert m is not None
    assert m.group(_CMD_GROUP) == "lf"
    assert m.group(_PARAM_GROUP) == '"blah"'
    m = _CMD_REGEX.match("%open 100")
    assert m is None


def test_opt() -> None:
    """Test '%opt'."""
    m = _CMD_REGEX.match("%opt log t")
    assert m is not None
    assert m.group(_CMD_GROUP) == "opt"
    assert m.group(_PARAM_GROUP) == "log"
    assert m.group(_OPT_GROUP) == "t"
    m = _CMD_REGEX.match("%opt run_on_load t")
    assert m is not None
    assert m.group(_CMD_GROUP) == "opt"
    assert m.group(_PARAM_GROUP) == "run_on_load"
    assert m.group(_OPT_GROUP) == "t"
    m = _CMD_REGEX.match("%opt time f")
    assert m is not None
    assert m.group(_CMD_GROUP) == "opt"
    assert m.group(_PARAM_GROUP) == "time"
    assert m.group(_OPT_GROUP) == "f"
    m = _CMD_REGEX.match("%opt tme true")
    assert m is not None
    assert not m.group(_PARAM_GROUP)


def test_break() -> None:
    """Test '%break'."""
    m = _CMD_REGEX.match("%break 122")
    assert m is not None
    assert m.group(_CMD_GROUP) == "break"
    assert m.group(_PARAM_GROUP) == "122"
    m = _CMD_REGEX.match("%bp")
    assert m is not None
    assert m.group(_CMD_GROUP) == "bp"
    m = _CMD_REGEX.match("%bra 805")
    assert m is None


def test_backtrace() -> None:
    """Test '%backtrace'."""
    m = _CMD_REGEX.match("%backtrace")
    assert m is not None
    assert m.group(_CMD_GROUP) == "backtrace"
    m = _CMD_REGEX.match("%bt")
    assert m is not None
    assert m.group(_CMD_GROUP) == "bt"


def test_continue() -> None:
    """Test '%continue'."""
    m = _CMD_REGEX.match("%continue")
    assert m is not None
    assert m.group(_CMD_GROUP) == "continue"
    m = _CMD_REGEX.match("%c")
    assert m is not None
    assert m.group(_CMD_GROUP) == "c"


def test_delete() -> None:
    """Test '%delete'."""
    m = _CMD_REGEX.match("%delete 805")
    assert m is not None
    assert m.group(_CMD_GROUP) == "delete"
    assert m.group(_PARAM_GROUP) == "805"
    m = _CMD_REGEX.match("%d")
    assert m is not None
    assert m.group(_CMD_GROUP) == "d"


def test_step() -> None:
    """Test '%step'."""
    m = _CMD_REGEX.match("%step")
    assert m is not None
    assert m.group(_CMD_GROUP) == "step"
    m = _CMD_REGEX.match("%s")
    assert m is not None
    assert m.group(_CMD_GROUP) == "s"


def test_vars() -> None:
    """Test '%vars'."""
    m = _CMD_REGEX.match("%vars")
    assert m is not None
    assert m.group(_CMD_GROUP) == "vars"
    m = _CMD_REGEX.match("%v")
    assert m is not None
    assert m.group(_CMD_GROUP) == "v"


def test_exit() -> None:
    """Test '%exit'."""
    m = _CMD_REGEX.match("%exit")
    assert m is not None
    assert m.group(_CMD_GROUP) == "exit"
    m = _CMD_REGEX.match("%e")
    assert m is not None
    assert m.group(_CMD_GROUP) == "e"
