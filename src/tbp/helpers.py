"""Contains helper functions used the different parts of tbp."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# I dislike having to do this pure ick here.
if sys.platform.startswith("win32"):
    # Windows doesn't have readline so as far as I can tell this is the
    # only way I can get something close.
    # https://stackoverflow.com/questions/51157443/pythons-readline-module-not-available-for-windows
    # https://github.com/pyreadline3/pyreadline3
    from pyreadline3 import Readline  # type: ignore   # noqa: PGH003

    readline = Readline()
else:
    # Including readline gives a *much* better editing experience.
    # https://docs.astral.sh/ruff/rules/unused-import/
    import readline  # pylint: disable=unused-import  # noqa: F401


if TYPE_CHECKING:
    from collections.abc import Callable

###############################################################################
# Logging
###############################################################################

logger: logging.Logger = logging.getLogger("tbp-log")
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def tbp_logger() -> logging.Logger:
    """Return the logger for all of tbp to use."""
    return logger


###############################################################################
# Common error builder.
###############################################################################


def build_error_string(source: str, message: str, column: int) -> str:
    """
    Create a useful error message.

    Arguments:
    ---------
    source  : The source line with the error.
    message : The error message.
    column  : The column in the source line with the error

    Builds an error like the following with the arrow pointing to the
    expression that had the error.

    Runtime Error: Error: #293 Syntax error in expression - expected integer value.
    20 LET D=RND("A")
    ---------^

    """
    return f"{message}\n{source}\n{"-" * column}^\n"


###############################################################################
# Short integers.
# Tiny BASIC only support 2-byte integers and Pythons are bigger than that.
###############################################################################
def short_int(x: int) -> int:
    """Transform a Python integer into a appropriately signed short."""
    # Lop off anything above 16-bits, which, surprisingly converts a Python
    # negatively signed number into an unsigned number. Python seems to use
    # signed integers for everything.
    x_stripped: int = x & 0x000000000000FFFF
    # Check if this a negative number.
    if x >> 15 != 0:
        # Kind of the opposite of two's compliment when you hack off bits.
        x_stripped -= 1
        # My bit twiddling skills end here.
        x_stripped -= 0xFFFF
    return x_stripped


###############################################################################
# Output
###############################################################################


# Note this is a private function.
def __default_output(message: str) -> None:
    """Print output from tbp."""
    # The end parameter to print defaults to end="\n" so you get the CRLF on
    # the output. The type for end is "str|None". When I set end=None, I was
    # getting extra CRLF in the output. Setting it to "" works. Odd.
    print(message, end="")


# If you would like to have your own output function, change this variable.
output_function: Callable[[str], None] = __default_output


def print_output(message: str) -> None:
    """Print output from tbp."""
    output_function(message)


###############################################################################
# Input
###############################################################################


def read_input(prompt: str) -> tuple[bool, str]:
    """Read input from the user."""
    result_str: str = ""
    result_flag: bool = True

    try:
        result_str = input(prompt)
    except (EOFError, KeyboardInterrupt):
        result_flag = False

    return result_flag, result_str


# The minimum number of entries in the valid_input list for limit_input.
MIN_INPUT_LEN = 2


def limit_input(prompt: str, valid_input: list[str]) -> tuple[bool, str]:
    """
    Input wrapper for limiting input.

    A simple wrapper around the builtin input function that only allows a
    limited set of values.

    Arguments:
    ---------
    prompt:  The prompt to ask the user.
    valid_input:  A list of strings that are valid input that has a minimum
    of two values.

    Returns:
    -------
    A tuple. The first field is a boolean, True indicating success. The second
    field is the user's input.
    If the first field is false, the user pressed CTRL+C or CTRL+D.

    Notes:
    -----
    - The comparisons are done using casefolding so input is case insensitive.
    - Index 0 in valid_input is the default entry so if the user enters only
      CRLF that value is returned.

    Example:
    -------
    yes_no:list[str] = ["y","n"]
    flag, result = limit_input("Do you want to overwrite the file? (Y/n)>", yes_no)

    """
    if len(valid_input) < MIN_INPUT_LEN:
        return False, ""

    # In order to do better matching, casefold the valid input strings.
    casefold_input = [x.casefold() for x in valid_input]
    keep_asking: bool = True
    result_flag: bool = True
    result_str: str = ""
    while keep_asking is True:
        try:
            # If the user entered just CRLF, we return the first item in
            # valid_input.
            if not (result_str := input(prompt)):
                result_str = valid_input[0]
                return result_flag, result_str
            if result_str.casefold() in casefold_input:
                return result_flag, result_str
            print_output("Invalid input.\n")
        except (EOFError, KeyboardInterrupt):
            result_flag = False
            keep_asking = False

    return False, ""


###############################################################################
# File saving and loading.
###############################################################################


# TODO(@John-Robbins): Figure out how this works on Windows.


def save_program(filename: str, program: str) -> bool:
    """Save the program to the filename."""
    try:
        the_file = Path(filename).expanduser()
        if the_file.exists() is True:
            yes_no: list[str] = ["y", "n"]
            overwrite, res = limit_input(
                "Do you want to overwrite the file? (Y/n)>",
                yes_no,
            )
            if (overwrite is False) or (res == "n"):
                return False
        with the_file.open(mode="w", encoding="utf-8") as f:
            f.write(program)
    except (RuntimeError, FileNotFoundError):
        print_output(f"CLE #12: Filename is invalid '{filename}'.\n")
        return False

    return True


def load_program(filename: str) -> str:
    """Load the program from filename."""
    info = ""
    try:
        the_file = Path(filename).expanduser()
        if the_file.exists() is False:
            print(f"CLE #13: File does not exist '{filename}'.")
            return info

        with the_file.open(mode="r", encoding="utf-8") as f:
            info = f.read()

    except (RuntimeError, FileNotFoundError):
        print(f"CLE #12: Filename is invalid '{filename}'.")

    return info
