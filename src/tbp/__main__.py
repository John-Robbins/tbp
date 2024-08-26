"""The entry point for tpb."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2004 John Robbins
###############################################################################
from __future__ import annotations

import argparse
import sys

from tbp.driver import Driver


def _command_line_processing() -> Driver.Options:
    """Handle the command line."""
    parser = argparse.ArgumentParser(
        description="Tiny BASIC in Python - github.com/John-Robbins/tbp",
        add_help=False,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )

    parser.add_argument(
        "-c",
        "--commands",
        type=str,
        default="",
        action="store",
        help="String of Tiny BASIC and/or command language instructions to "
        "execute. Use ^ to separate individual commands.",
    )
    parser.add_argument(
        "-nl",
        "--nologo",
        action="store_true",
        help="Do not display the glorious tbp logo 😿",
    )
    parser.add_argument(
        "file",
        default="",
        type=str,
        nargs="?",
        action="store",
        help="Optional Tiny BASIC in Python program to run",
    )

    args = parser.parse_args()

    opts: Driver.Options = Driver.Options(
        file=args.file,
        commands=args.commands,
        nologo=args.nologo,
    )

    return opts


def main() -> int:
    """Start tbp."""
    opts: Driver.Options = _command_line_processing()

    driver: Driver = Driver()

    result: int = driver.party_like_it_is_1976(opts)

    return result


if __name__ == "__main__":
    res: int = main()
    sys.exit(res)
