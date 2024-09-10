"""The scanner class for tokenizing a string."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

from typing import cast

from tbp.errors import TbpSyntaxError
from tbp.helpers import tbp_logger
from tbp.tokens import Token, TokenType


class Scanner:
    """
    The lexical scanner for tbp.

    This class is designed to handle parsing a single Tiny BASIC line of source
    code at a time. That way we isolate all the logic of deciding how the
    interpreter does its job.

    By default, the Scanner class will add a CRLF onto the line being scanned
    if one is not already on the character stream.
    """

    def __init__(self: Scanner) -> None:
        """Initialize the scanner class."""
        # The line we are parsing.
        self._source_line: str = ""
        # The current position in the line.
        self._current_index: int = 0
        # The length of the line.
        self._source_length: int = 0
        # The start of the current lexeme we are processing.
        self._lexeme_start: int = 0
        # The lexeme we build up as we skip spaces.
        self._current_lexeme: str = ""
        # The line number if present, 0 if not.
        self._line_number = 0
        # The tokens we will be returning.
        self._tokens: list[Token] = list[Token]()
        # Grab the logger so we have it in the class.
        self._logger = tbp_logger()

    def scan_tokens(self: Scanner, source: str) -> list[Token]:
        """
        Scan a Tiny BASIC string and return a list of tokens.

        Parameters
        ----------
        source:
            The tiny BASIC line to scan.

        Returns
        -------
            The list of Tokens scanned from the source line.

        Exceptions
        ----------
        ValueError:
            If the source parameter is empty or has zero length.

        """
        # Check the parameter.
        # Pylance reports a problem with 'source is None` that it is always
        # false when that is not true.

        # pyright: ignore[reportUnnecessaryComparison]
        if source is None or len(source) == 0:
            msg: str = "source argument cannot be empty"
            raise ValueError(msg)

        self._logger.debug("Scanning: `%s`", source)

        # Make sure there's a CRLF on the end of the line. This helps so much
        # with testing I made it permanent.
        src_len = len(source)
        if source[src_len - 1] != "\n":
            source += "\n"

        # Clear out any old data.
        self._tokens = list[Token]()
        self._current_index = 0
        self._lexeme_start = 0
        self._current_lexeme = ""
        self._source_line = source
        self._source_length = len(source)
        self._line_number = 0

        # Line numbers are very important in Tiny BASIC.
        self._find_line_number()

        # Now it's time to lexify this string!
        while self._is_at_end() is False:
            # Point to the start of the lexeme.
            self._lexeme_start = self._current_index
            # Let's grab the next one.
            self._scan_token()
            self._current_lexeme = ""
            # Advance to get the next character to work with.
            self._advance()

        # Put on the finishing touch, the sentinel.
        self._lexeme_start = self._current_index
        self._current_lexeme = "\n"
        self._add_token(TokenType.CRLF)

        return self._tokens

    def _scan_token(self: Scanner) -> None:  # noqa: C901, PLR0912
        """Scan in the current lexeme and figure out what it is."""
        # Grab the current character, which is upper case.
        curr_character = self._current()
        self._current_lexeme = self._current_raw()
        match curr_character:
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case ",":
                self._add_token(TokenType.COMMA)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case ":":
                self._add_token(TokenType.COLON)
            case "*":
                self._add_token(TokenType.STAR)
            case "/":
                self._add_token(TokenType.SLASH)
            case "=":
                self._add_token(TokenType.EQUAL)
            case "<":
                # A '<' can be '<=' (LESS_EQUAL) or "<>" (NOT_EQUAL)
                if self._match("=") is True:
                    self._add_token(TokenType.LESS_EQUAL)
                elif self._match(">") is True:
                    self._add_token(TokenType.NOT_EQUAL)
                else:
                    self._add_token(TokenType.LESS)
            case ">":
                # A '>' can be '>=' (GREATER_EQUAL) or '><' (NOT_EQUAL)
                if self._match("=") is True:
                    self._add_token(TokenType.GREATER_EQUAL)
                elif self._match("<") is True:
                    self._add_token(TokenType.NOT_EQUAL)
                else:
                    self._add_token(TokenType.GREATER)
            case '"':
                self._string()
            case _:
                if curr_character.isdigit() is True:
                    self._number()
                elif curr_character.isalpha() is True:
                    self._handle_keyword_or_identifier(curr_character)
                else:
                    self._report_error(
                        "Error #293: Syntax error - unexpected expression : "
                        f"'{curr_character}'",
                    )

    ###########################################################################
    # Methods that move the index, get the current character, and see if there
    # are matches.
    ###########################################################################

    def _is_at_end(self: Scanner) -> bool:
        """Return true if we are at the end of the line."""
        return self._source_line[self._current_index] == "\n"

    def _advance(self: Scanner) -> str:
        """Skipping whitespace, return the next character in the string."""
        # Go nowhere if we are at the end.
        if self._is_at_end() is True:
            return "\0"

        # Prepare to read the next one.
        self._current_index += 1
        if self._is_at_end() is True:
            return "\0"

        self._skip_whitespace()

        next_char: str = self._current()
        self._current_lexeme += self._current_raw()

        # Return the next character.
        return next_char

    def _advance_preserving_whitespace(self: Scanner) -> str:
        """Return the next character in the string."""
        # Prepare to read the next one.
        self._current_index += 1
        if self._is_at_end() is True:
            return "\0"

        next_char: str = self._current()
        self._current_lexeme += self._current_raw()

        # Return the next character.
        return next_char

    def _back_up(self: Scanner) -> None:
        """Give back the current token."""
        if self._current_index > 0:
            self._current_index -= 1

    def _skip_whitespace(self: Scanner) -> None:
        """Skip any whitespace."""
        if self._is_at_end() is True:
            return
        curr_char: str = self._current()
        while curr_char.isspace():
            self._current_index += 1
            if self._is_at_end() is True:
                return
            curr_char = self._current()

    def _match(self: Scanner, expected: str) -> bool:
        """Check the next character to see if it matches."""
        if self._peek() != expected:
            return False
        # It's a match so account for us eating it.
        self._advance()
        return True

    def _current(self: Scanner) -> str:
        """Return the current character in uppercase form."""
        return self._current_raw().upper()

    def _current_raw(self: Scanner) -> str:
        """Return the current character as is."""
        if self._is_at_end() is True:
            return "\0"
        return self._source_line[self._current_index]

    def _peek(self: Scanner) -> str:
        """Peeks at the next character."""
        if self._is_at_end() is True:
            return "\0"
        return self._source_line[self._current_index + 1].upper()

    ###########################################################################
    # Methods find line numbers, strings, keywords, and comments.
    ###########################################################################

    def _string(self: Scanner) -> None:
        """Get the string out of the token stream."""
        # Save off the column of the opening '"' so we can report where the
        # string started.
        string_start: int = self._current_index

        # We get called pointing to the first double quote of the string, so
        # we are going to advance to get into the string.
        self._advance_preserving_whitespace()

        # We've bumped up one character past the opening quote. Do a check if
        # this is an empty string.
        if (self._source_line[self._lexeme_start] == '"') and (
            self._source_line[self._current_index] == '"'
        ):
            self._add_token(TokenType.STRING, "")
            return

        # Grind through everything up to the closing quote making sure not to
        # go off the end of the string.
        while (self._peek() != '"') and (self._is_at_end() is False):
            self._advance_preserving_whitespace()

        # Did we go off the end of the line?
        if self._is_at_end() is True:
            self._report_error(
                f"Error #331: Unterminated string (started at position {string_start})",
            )

        # Eat the closing quote we just found.
        self._advance()

        value = self._source_line[self._lexeme_start + 1 : self._current_index]
        self._add_token(TokenType.STRING, value)

    def _check_keyword(
        self: Scanner,
        keyword: str,
        token_type: TokenType,
    ) -> bool:
        # We are going to do some peeking here, but I don't want to be messing
        # with the real index values into our source string. Hence, this method
        # will do all the checking without relying on other methods.

        # The index we are starting from.
        temp_index: int = self._current_index
        key_len: int = len(keyword)

        self._current_lexeme = ""

        # Build up enough characters to do a comparison.
        char_count: int = 0
        while char_count < key_len:
            # What is this character? A space of some kind?
            curr_char = self._source_line[temp_index].upper()
            if curr_char.isspace():
                temp_index += 1
                if temp_index >= self._source_length:
                    # Nope, we've gone off the deep end.
                    return False
            elif (curr_char.isalpha() is True) and (keyword[char_count] == curr_char):
                # Poke this char into the compare string.
                self._current_lexeme += self._source_line[temp_index]
                char_count += 1
                temp_index += 1
                if temp_index >= self._source_length:
                    # Nope, we've gone off the deep end.
                    return False
            else:
                # It's not a space or alphanumeric so pull the rip cord.
                break

        # Did we scoop up enough characters to do a comparison?
        if char_count != key_len:
            self._current_lexeme = ""
            return False

        # We found a keyword, but if the token type is Token.EOF, we found
        # PRETURN, which is a pain in the butt so return false.
        if token_type == TokenType.EOF:
            self._current_lexeme = ""
            return True

        # Move the main tracker past the keyword.
        self._current_index = temp_index - 1
        self._add_token(token_type)

        return True

    def _extract_number(self: Scanner) -> str:
        """Extract a number skipping whitespace."""
        self._skip_whitespace()

        # The raw number string this method builds up.
        raw_number: str = ""

        curr_char: str = self._current()
        self._current_lexeme += curr_char

        # Collect the digits?
        while ((curr_char.isdigit() is True) or (curr_char in {" ", "\r", "\t"})) and (
            self._is_at_end() is False
        ):
            if curr_char.isdigit():
                raw_number += curr_char

            # Advance past the digit or white space.
            curr_char = self._advance()

        # That last _advance() call added the next character to the lexeme
        # string, so I'm going to remove it. Ick. This makes me feel dirty.
        if self._is_at_end() is False:
            self._current_lexeme = self._current_lexeme[:-1]

        return raw_number

    def _number(self: Scanner) -> None:
        """Get the number out of the token string."""
        self._current_lexeme = ""
        raw_number: str = self._extract_number()
        self._add_token(TokenType.NUMBER, int(raw_number))
        # In order to get the number, we end up reading past the number so we
        # ensure we get all digits. All the design here is predicated on the
        # idea that when a lexeme is processed, the current index is pointing
        # directly at it. Thus, I need to back up one to keep the index in the
        # right spot.
        self._back_up()

    def _find_line_number(self: Scanner) -> None:
        """
        If present, scans in the line number.

        In Tiny BASIC, the documentation states that line numbers can be any
        form with spaces. Thus, '100', '1 0 0', '   100' and '1      00'
        are all the same number.

        """
        raw_number: str = self._extract_number()

        # Do we have a possible number?
        if len(raw_number) > 0:
            # Add the line number token.
            self._line_number = int(raw_number)
            self._add_token(TokenType.LINE_NUMBER, self._line_number)

    def _handle_keyword_or_identifier(  # noqa: C901, PLR0912
        self: Scanner,
        first_char: str,
    ) -> None:
        # The main scanner loop has us sitting on the first alphabetical
        # character of a keyword, or an identifier.
        was_keyword: bool = False

        match first_char:
            case "C":
                was_keyword = self._check_keyword("CLEAR", TokenType.CLEAR)
            case "E":
                was_keyword = self._check_keyword("END", TokenType.END)
            case "G":
                if (
                    was_keyword := self._check_keyword("GOTO", TokenType.GOTO)
                ) is False:
                    was_keyword = self._check_keyword("GOSUB", TokenType.GOSUB)
            case "I":
                if (was_keyword := self._check_keyword("IF", TokenType.IF)) is False:
                    was_keyword = self._check_keyword("INPUT", TokenType.INPUT)
            case "L":
                if (was_keyword := self._check_keyword("LET", TokenType.LET)) is False:
                    was_keyword = self._check_keyword("LIST", TokenType.LIST)
            case "P":
                if (
                    was_keyword := self._check_keyword("PRINT", TokenType.PRINT)
                ) is False:
                    # Ugh! I've messed something up pretty good. A statement
                    # like "IF X >P RETURN" is a mess to scan because
                    # "IF X > PR ETURN" can be the result, which is invalid.
                    # Hence, I'll check if it looks like "PRETURN" and if so,
                    # fail the result. I feel so amazingly dirty doing the
                    # check this way. By passing in the TokenType.EOF, that
                    # tells _check_keyword to ignore the result, but return
                    # True that we scanned the result, and it's PRETURN.
                    if (
                        was_keyword := self._check_keyword("PRETURN", TokenType.EOF)
                    ) is True:
                        was_keyword = False
                    else:
                        was_keyword = self._check_keyword("PR", TokenType.PRINT)
            case "R":
                was_keyword = self._check_keyword("RUN", TokenType.RUN)
                if was_keyword is False:
                    was_keyword = self._check_keyword("RETURN", TokenType.RETURN)
                if was_keyword is False:
                    was_keyword = self._check_keyword("RND", TokenType.RND)
                if (
                    was_keyword is False
                    and (was_keyword := self._check_keyword("REM", TokenType.REM))
                    is True
                ):
                    # We know this is a REM comment so handle it here.
                    self._read_comment()
            case "T":
                was_keyword = self._check_keyword("THEN", TokenType.THEN)
            case "U":
                was_keyword = self._check_keyword("USR", TokenType.USR)
            case _:
                pass

        # If a keyword wasn't processed, it's an identifier.
        if was_keyword is False:
            self._current_lexeme = self._current_raw()
            self._add_token(TokenType.IDENTIFIER, first_char)

    def _read_comment(self: Scanner) -> None:
        """Read the content after a REM and creates a comment token."""
        # The index is sitting on the 'M" in REM. While I could call _advance()
        # here, that will skip whitespace at the start of the comment. My take
        # on the comment string is that it is everything on the line after the
        # 'M'.
        self._advance_preserving_whitespace()
        # I hate writing to self._current_index outside of _advance.
        start_pos = self._current_index
        count = start_pos + (self._source_length - start_pos - 1)
        comment: str = self._source_line[start_pos:count]
        self._add_token(TokenType.COMMENT, comment)
        # Now move past the comment.
        self._current_index += len(comment)

    ###########################################################################
    # Support methods.
    ###########################################################################

    def _add_token(
        self: Scanner,
        token_type: TokenType,
        literal: str | int = cast(str, None),
    ) -> None:
        self._tokens.append(
            Token(
                token_type,
                lexeme=self._current_lexeme,
                line=self._line_number,
                column=self._lexeme_start,
                value=literal,
            ),
        )

    def _report_error(self: Scanner, message: str) -> None:
        """Report an error to the user."""
        error: TbpSyntaxError = TbpSyntaxError(
            self._line_number,
            self._current_index,
            message,
        )
        raise error
