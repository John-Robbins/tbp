"""All the tokens returned by the scanner."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

from enum import Enum, auto
from typing import cast


class TokenType(Enum):
    """All the lexical token types used in tbp."""

    # Reserved words and keywords.
    CLEAR = auto()
    END = auto()
    GOTO = auto()
    GOSUB = auto()
    IF = auto()
    INPUT = auto()
    LET = auto()
    LIST = auto()
    PRINT = auto()
    REM = auto()
    RETURN = auto()
    RUN = auto()
    THEN = auto()
    RND = auto()
    USR = auto()

    # Single character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    GREATER = auto()
    LESS = auto()
    EQUAL = auto()

    # Two character tokens.
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    # Tiny BASIC supports two not equal lexemes, '<>' and '><'. The scanner
    # will handle the difference between the two.
    NOT_EQUAL = auto()

    # Special values.
    # The Tiny BASIC line number.
    LINE_NUMBER = auto()
    # The comment text after a REM instruction.
    COMMENT = auto()

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()

    # Sentinels for line and file, respectively.
    CRLF = auto()
    EOF = auto()


class Token:
    """A lexical token in the Tiny BASIC language."""

    def __init__(
        self: Token,
        tbp_type: TokenType,
        lexeme: str,
        line: int,
        column: int,
        value: str | int = cast(str, None),
    ) -> None:
        """
        Initialize the Token class.

        Parameters
        ----------
        tbp_type:
            The type of token for this instance.
        lexeme:
            The text for the token. For example, if this is a THEN token, the
            lexeme would be "THEN".
        line:
            The Tiny BASIC line number. If not present this value is 0
            indicating a direct execution statement.
        column:
            The column for the token.
        value:
            If this is a literal token, the value of the token.

        """
        self.tbp_type: TokenType = tbp_type
        self.lexeme: str = lexeme
        self.line = line
        self.column: int = column
        self.value: str | int = value

    def __repr__(self: Token) -> str:
        """Return a string representation of the token instance."""
        # Ensure the types are padded so they are lined up when output and also
        # strip off the class name.
        name: str = str(self.tbp_type)
        name = name[len("TokenType") + 1 :]
        return f"[{name} ({self.line},{self.column})]"


###############################################################################
# Helper function to put scanner tokens into a string.
###############################################################################


def tokens_to_string(tokens: list[Token]) -> str:
    """
    Convert the array of lexical tokens into a string.

    Parameters
    ----------
    tokens:
        The list of tokens to process.

    Returns
    -------
        A string of all the tokens separated by CRLF.

    """
    ret_str: str = ""
    return ret_str.join((str(item)) for item in tokens)
