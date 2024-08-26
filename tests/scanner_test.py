"""Unit tests for the Scanner class."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2004 John Robbins
###############################################################################

from __future__ import annotations

import io
from typing import TYPE_CHECKING, cast

import pytest

from tbp.errors import TbpSyntaxError
from tbp.scanner import Scanner
from tbp.tokens import TokenType
from tests.programs import FLASHCARD_PROGRAM, MANIC_PROGRAM, TICTACTOE_PROGRAM

if TYPE_CHECKING:
    from tbp.tokens import Token


def test_initialization() -> None:
    """Test to see if the scanner initializes."""
    scan: Scanner = Scanner()
    assert scan is not None


def test_invalid_param_to_scan_tokens() -> None:
    """Make sure we are throwing the exception on invalid parameters."""
    scan: Scanner = Scanner()
    empty_str: str = ""
    none_str: str = cast(str, None)
    with pytest.raises(ValueError, match="source argument cannot be empty"):
        scan.scan_tokens(empty_str)

    with pytest.raises(ValueError, match="source argument cannot be empty"):
        scan.scan_tokens(none_str)


def test_single_char_scan() -> None:
    """Check if single character tokens parse correctly."""
    scan: Scanner = Scanner()
    tokens: list[Token] = scan.scan_tokens("()")
    # Don't forget to account for the CRLF token. :)
    assert len(tokens) == 3
    assert tokens[0].tbp_type == TokenType.LEFT_PAREN
    assert tokens[1].tbp_type == TokenType.RIGHT_PAREN
    assert tokens[2].tbp_type == TokenType.CRLF


def test_more_single_char_scan() -> None:
    """More single characters scan tests."""
    scan: Scanner = Scanner()
    source: str = ",-+;*/"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 7
    assert tokens[0].tbp_type == TokenType.COMMA
    assert tokens[1].tbp_type == TokenType.MINUS
    assert tokens[2].tbp_type == TokenType.PLUS
    assert tokens[3].tbp_type == TokenType.SEMICOLON
    assert tokens[4].tbp_type == TokenType.STAR
    assert tokens[5].tbp_type == TokenType.SLASH
    assert tokens[6].tbp_type == TokenType.CRLF


def test_greater_char() -> None:
    """Test '> >= ><'."""
    scan: Scanner = Scanner()
    source: str = "> >= ><"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.GREATER
    assert tokens[1].tbp_type == TokenType.GREATER_EQUAL
    assert tokens[2].tbp_type == TokenType.NOT_EQUAL
    assert tokens[3].tbp_type == TokenType.CRLF


def test_less_char() -> None:
    """Test '< <= <>'."""
    scan: Scanner = Scanner()
    source: str = "< <= <>"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.LESS
    assert tokens[1].tbp_type == TokenType.LESS_EQUAL
    assert tokens[2].tbp_type == TokenType.NOT_EQUAL
    assert tokens[3].tbp_type == TokenType.CRLF


def test_peek_end() -> None:
    """Test '<'."""
    scan: Scanner = Scanner()
    source: str = "<"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 2
    assert tokens[0].tbp_type == TokenType.LESS


def test_simple_number() -> None:
    """Test a single number."""
    scan: Scanner = Scanner()
    source: str = "100"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 2
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[0].value == 100
    assert tokens[1].tbp_type == TokenType.CRLF


def test_simple_string() -> None:
    """Simple string test."""
    scan: Scanner = Scanner()
    source: str = '"Hi!"'
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 2
    assert tokens[0].tbp_type == TokenType.STRING
    assert tokens[0].value == "Hi!"
    assert tokens[1].tbp_type == TokenType.CRLF


def test_unterminated_string() -> None:
    """Unterminated string test."""
    scan: Scanner = Scanner()
    source: str = '"Hi'
    with pytest.raises(TbpSyntaxError):
        scan.scan_tokens(source)


def test_line_numbers() -> None:
    """Test weird line numbers."""

    def execute_test(source: str) -> None:
        scan: Scanner = Scanner()
        tokens = scan.scan_tokens(source)
        assert len(tokens) == 3
        assert tokens[0].tbp_type == TokenType.LINE_NUMBER
        assert tokens[0].value == 100
        assert tokens[1].tbp_type == TokenType.CLEAR
        assert tokens[2].tbp_type == TokenType.CRLF

    execute_test("100clear")
    execute_test("1 0 0CLEAR")
    execute_test("    100       CLEAR")
    execute_test("    1 0 0       C L E A R              ")


def test_simple_identifiers() -> None:
    """Test simple identifiers."""
    scan: Scanner = Scanner()
    source: str = "CLEAR THEN a"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.CLEAR
    assert tokens[1].tbp_type == TokenType.THEN
    assert tokens[2].tbp_type == TokenType.IDENTIFIER
    assert tokens[2].lexeme == "a"


def test_invalid_char() -> None:
    """Make sure we are throwing the exception on invalid characters."""
    scan: Scanner = Scanner()
    bad_str: str = "111 LET %=2"
    with pytest.raises(
        TbpSyntaxError,
        match="'%'",
    ):
        scan.scan_tokens(bad_str)


def test_simple_goto_identifiers() -> None:
    """Test simple goto identifiers."""
    scan: Scanner = Scanner()
    source: str = "111 goto 200"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[0].value == 111
    assert tokens[1].tbp_type == TokenType.GOTO
    assert tokens[1].lexeme == "goto"
    assert tokens[2].tbp_type == TokenType.NUMBER
    assert tokens[2].value == 200


def test_just_go_is_two_identifiers() -> None:
    """Test simple gosub identifiers."""
    scan: Scanner = Scanner()
    source: str = "111 GO 200"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 5
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[0].value == 111
    assert tokens[1].tbp_type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "G"
    assert tokens[2].tbp_type == TokenType.IDENTIFIER
    assert tokens[2].lexeme == "O"
    assert tokens[3].tbp_type == TokenType.NUMBER
    assert tokens[3].value == 200


def test_simple_gosub_identifiers() -> None:
    """Test simple gosub identifiers."""
    scan: Scanner = Scanner()
    source: str = "111 GOSUB 200"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[0].value == 111
    assert tokens[1].tbp_type == TokenType.GOSUB
    assert tokens[2].tbp_type == TokenType.NUMBER
    assert tokens[2].value == 200


def test_simple_gosub_identifiers_with_spaces() -> None:
    """Test simple gosub identifiers."""
    scan: Scanner = Scanner()
    source: str = " 1 1 1 G O S U B  2 0    0 "
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[0].value == 111
    assert tokens[1].tbp_type == TokenType.GOSUB
    assert tokens[2].tbp_type == TokenType.NUMBER
    assert tokens[2].value == 200


def test_simple_comment() -> None:
    """Test a comment."""
    scan: Scanner = Scanner()
    source: str = "111 REM Howdy!"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[0].value == 111
    assert tokens[1].tbp_type == TokenType.REM
    assert tokens[2].tbp_type == TokenType.COMMENT
    assert tokens[2].value == " Howdy!"


def test_all_keywords() -> None:
    """Test all keywords."""
    scan: Scanner = Scanner()
    source: str = "clear end goto gosub if input let list print pr return run then rnd"
    source += " usr"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 16
    assert tokens[0].tbp_type == TokenType.CLEAR
    assert tokens[1].tbp_type == TokenType.END
    assert tokens[2].tbp_type == TokenType.GOTO
    assert tokens[3].tbp_type == TokenType.GOSUB
    assert tokens[4].tbp_type == TokenType.IF
    assert tokens[5].tbp_type == TokenType.INPUT
    assert tokens[6].tbp_type == TokenType.LET
    assert tokens[7].tbp_type == TokenType.LIST
    assert tokens[8].tbp_type == TokenType.PRINT
    assert tokens[9].tbp_type == TokenType.PRINT
    assert tokens[10].tbp_type == TokenType.RETURN
    assert tokens[11].tbp_type == TokenType.RUN
    assert tokens[12].tbp_type == TokenType.THEN
    assert tokens[13].tbp_type == TokenType.RND
    assert tokens[14].tbp_type == TokenType.USR


def test_some_keywords_no_spaces() -> None:
    """Test some keywords with no spaces."""
    scan: Scanner = Scanner()
    source: str = "clearend"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 3
    assert tokens[0].tbp_type == TokenType.CLEAR
    assert tokens[1].tbp_type == TokenType.END
    assert tokens[2].tbp_type == TokenType.CRLF


def test_all_keywords_no_spaces() -> None:
    """Test all keywords with no spaces."""
    scan: Scanner = Scanner()
    source: str = "clearendgotogosubifinputletlistprintprreturnrunthenrndusr"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 16
    assert tokens[0].tbp_type == TokenType.CLEAR
    assert tokens[1].tbp_type == TokenType.END
    assert tokens[2].tbp_type == TokenType.GOTO
    assert tokens[3].tbp_type == TokenType.GOSUB
    assert tokens[4].tbp_type == TokenType.IF
    assert tokens[5].tbp_type == TokenType.INPUT
    assert tokens[6].tbp_type == TokenType.LET
    assert tokens[7].tbp_type == TokenType.LIST
    assert tokens[8].tbp_type == TokenType.PRINT
    assert tokens[9].tbp_type == TokenType.PRINT
    assert tokens[10].tbp_type == TokenType.RETURN
    assert tokens[11].tbp_type == TokenType.RUN
    assert tokens[12].tbp_type == TokenType.THEN
    assert tokens[13].tbp_type == TokenType.RND
    assert tokens[14].tbp_type == TokenType.USR


def test_all_keywords_spaces_everywhere() -> None:
    """Test all keywords with no spaces."""
    scan: Scanner = Scanner()
    source: str = (
        "c l e a r e n d g o t o g o s u b i f i n p u t l e t "
        "l i s t p r i n t p r r e t u r n r u n t h e n r n d u s r "
    )
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 16
    assert tokens[0].tbp_type == TokenType.CLEAR
    assert tokens[1].tbp_type == TokenType.END
    assert tokens[2].tbp_type == TokenType.GOTO
    assert tokens[3].tbp_type == TokenType.GOSUB
    assert tokens[4].tbp_type == TokenType.IF
    assert tokens[5].tbp_type == TokenType.INPUT
    assert tokens[6].tbp_type == TokenType.LET
    assert tokens[7].tbp_type == TokenType.LIST
    assert tokens[8].tbp_type == TokenType.PRINT
    assert tokens[9].tbp_type == TokenType.PRINT
    assert tokens[10].tbp_type == TokenType.RETURN
    assert tokens[11].tbp_type == TokenType.RUN
    assert tokens[12].tbp_type == TokenType.THEN
    assert tokens[13].tbp_type == TokenType.RND
    assert tokens[14].tbp_type == TokenType.USR


def test_print_pr_keywords() -> None:
    """Test the PRINT and PR scanning."""

    def runit(source: str) -> list[Token]:
        scan: Scanner = Scanner()
        return scan.scan_tokens(source)

    tokens: list[Token] = runit("PR")
    assert len(tokens) == 2
    assert tokens[0].tbp_type == TokenType.PRINT
    assert tokens[1].tbp_type == TokenType.CRLF

    tokens = runit("PRINT")
    assert len(tokens) == 2
    assert tokens[0].tbp_type == TokenType.PRINT
    assert tokens[1].tbp_type == TokenType.CRLF

    tokens = runit("PRI")
    assert len(tokens) == 3
    assert tokens[0].tbp_type == TokenType.PRINT
    assert tokens[1].tbp_type == TokenType.IDENTIFIER
    assert tokens[1].value == "I"
    assert tokens[2].tbp_type == TokenType.CRLF

    tokens = runit('PR "PAM!"')
    assert len(tokens) == 3
    assert tokens[0].tbp_type == TokenType.PRINT
    assert tokens[1].tbp_type == TokenType.STRING
    assert tokens[1].value == "PAM!"
    assert tokens[2].tbp_type == TokenType.CRLF

    tokens = runit("PR 10,20;30")
    assert len(tokens) == 7
    assert tokens[0].tbp_type == TokenType.PRINT
    assert tokens[1].tbp_type == TokenType.NUMBER
    assert tokens[1].value == 10
    assert tokens[2].tbp_type == TokenType.COMMA
    assert tokens[3].tbp_type == TokenType.NUMBER
    assert tokens[3].value == 20
    assert tokens[4].tbp_type == TokenType.SEMICOLON
    assert tokens[5].tbp_type == TokenType.NUMBER
    assert tokens[5].value == 30
    assert tokens[6].tbp_type == TokenType.CRLF


def test_keyword_split_comment() -> None:
    """Test a keyword split at the end of the line."""

    def runit(source: str) -> None:
        scan: Scanner = Scanner()
        tokens: list[Token] = scan.scan_tokens(source)
        for (
            i,
            item,
        ) in enumerate(tokens):
            if item.tbp_type != TokenType.CRLF:
                assert item.tbp_type == TokenType.IDENTIFIER
                assert item.value == source[i]

    runit("GO")
    runit("CLE")
    runit("INP")
    runit("LE")
    runit("LIS")
    # Note: Can't test `PRIN` as that resolves to PRINT IDENTIFIER(I).
    runit("RU")
    runit("RETUR")
    runit("RN")
    runit("RE")
    runit("THE")
    runit("US")


def test_full_line() -> None:
    """Test a complete line."""

    def runit(source: str) -> None:
        scan: Scanner = Scanner()
        tokens: list[Token] = scan.scan_tokens(source)
        assert len(tokens) == 12
        assert tokens[0].tbp_type == TokenType.LINE_NUMBER
        assert tokens[0].value == 100
        assert tokens[1].tbp_type == TokenType.IF
        assert tokens[2].tbp_type == TokenType.RND
        assert tokens[3].tbp_type == TokenType.LEFT_PAREN
        assert tokens[4].tbp_type == TokenType.NUMBER
        assert tokens[4].value == 10
        assert tokens[5].tbp_type == TokenType.RIGHT_PAREN
        assert tokens[6].tbp_type == TokenType.GREATER
        assert tokens[7].tbp_type == TokenType.NUMBER
        assert tokens[7].value == 100
        assert tokens[8].tbp_type == TokenType.THEN
        assert tokens[9].tbp_type == TokenType.GOSUB
        assert tokens[10].tbp_type == TokenType.NUMBER
        assert tokens[10].value == 20

    runit("100 IF RND(10) > 100 THEN GOSUB 20")
    runit(" 1 0 0   I F   R N D ( 1 0 )   >   1 0 0   T H E N   G O S U B   2 0   ")
    runit("100 I          F RND(10) > 100 TH                  EN GO             SUB 20")


def test_another_full_line() -> None:
    """Test a complete line."""
    scan: Scanner = Scanner()
    source: str = "1011 IFA+B+C+D+E+F+G<J GOTO 60"
    tokens: list[Token] = scan.scan_tokens(source)
    assert len(tokens) == 20
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[0].value == 1011
    assert tokens[1].tbp_type == TokenType.IF
    assert tokens[2].tbp_type == TokenType.IDENTIFIER
    assert tokens[2].value == "A"
    assert tokens[3].tbp_type == TokenType.PLUS
    assert tokens[4].tbp_type == TokenType.IDENTIFIER
    assert tokens[4].value == "B"
    assert tokens[5].tbp_type == TokenType.PLUS
    assert tokens[6].tbp_type == TokenType.IDENTIFIER
    assert tokens[6].value == "C"
    assert tokens[7].tbp_type == TokenType.PLUS
    assert tokens[8].tbp_type == TokenType.IDENTIFIER
    assert tokens[8].value == "D"
    assert tokens[9].tbp_type == TokenType.PLUS
    assert tokens[10].tbp_type == TokenType.IDENTIFIER
    assert tokens[10].value == "E"
    assert tokens[11].tbp_type == TokenType.PLUS
    assert tokens[12].tbp_type == TokenType.IDENTIFIER
    assert tokens[12].value == "F"
    assert tokens[13].tbp_type == TokenType.PLUS
    assert tokens[14].tbp_type == TokenType.IDENTIFIER
    assert tokens[14].value == "G"
    assert tokens[15].tbp_type == TokenType.LESS
    assert tokens[16].tbp_type == TokenType.IDENTIFIER
    assert tokens[16].value == "J"
    assert tokens[17].tbp_type == TokenType.GOTO
    assert tokens[18].tbp_type == TokenType.NUMBER
    assert tokens[18].value == 60


def test_let_usage() -> None:
    """Test how LET works."""

    def runit(source: str, num_tokens: int) -> None:
        scan: Scanner = Scanner()
        tokens: list[Token] = scan.scan_tokens(source)
        assert len(tokens) == num_tokens

    runit("LET A=99", 5)
    runit("B=5", 4)


def test_lexeme_values() -> None:
    """Test some keywords with no spaces."""
    scan: Scanner = Scanner()
    source: str = "LIST 100,200 RETURN"
    tokens = scan.scan_tokens(source)
    assert len(tokens) == 6
    assert tokens[0].tbp_type == TokenType.LIST
    assert tokens[0].lexeme == "LIST"
    assert tokens[1].tbp_type == TokenType.NUMBER
    assert tokens[1].lexeme == "100"
    assert tokens[1].value == 100
    assert tokens[2].tbp_type == TokenType.COMMA
    assert tokens[3].tbp_type == TokenType.NUMBER
    assert tokens[3].lexeme == "200"
    assert tokens[3].value == 200
    assert tokens[4].lexeme == "RETURN"
    assert tokens[5].tbp_type == TokenType.CRLF


def test_if_rel_ops_values() -> None:
    """Test relation operator lexemes are correct."""

    def runit(source: str, t_type: TokenType, lexeme: str) -> None:
        scan: Scanner = Scanner()
        tokens = scan.scan_tokens(source)
        assert tokens[2].tbp_type == t_type
        assert tokens[2].lexeme == lexeme

    runit("IF I = J PRINT Q,R", TokenType.EQUAL, "=")
    runit("IF I < J PRINT Q,R", TokenType.LESS, "<")
    runit("IF I > J PRINT Q,R", TokenType.GREATER, ">")
    runit("IF I <= J PRINT Q,R", TokenType.LESS_EQUAL, "<=")
    runit("IF I >= J PRINT Q,R", TokenType.GREATER_EQUAL, ">=")
    runit("IF I <> J PRINT Q,R", TokenType.NOT_EQUAL, "<>")
    runit("IF I >< J PRINT Q,R", TokenType.NOT_EQUAL, "><")


def test_print_strings_seps() -> None:
    """Test '3100 PRINT A;" ";'."""
    scan: Scanner = Scanner()
    tokens = scan.scan_tokens('3100 PRINT A;" ";')
    assert len(tokens) == 7
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[1].tbp_type == TokenType.PRINT
    assert tokens[2].tbp_type == TokenType.IDENTIFIER
    assert tokens[2].lexeme == "A"
    assert tokens[3].tbp_type == TokenType.SEMICOLON
    assert tokens[4].tbp_type == TokenType.STRING
    assert tokens[5].tbp_type == TokenType.SEMICOLON


def test_print_empty_string() -> None:
    """Test '3100 PRINT ""'."""
    scan: Scanner = Scanner()
    tokens = scan.scan_tokens('3100 PRINT ""')
    assert len(tokens) == 4
    assert tokens[0].tbp_type == TokenType.LINE_NUMBER
    assert tokens[1].tbp_type == TokenType.PRINT
    assert tokens[2].tbp_type == TokenType.STRING
    assert tokens[2].lexeme == '""'


def test_flashcard_program() -> None:
    """Scan the whole Flash Card program."""
    # logger: logging.Logger = logging.getLogger("test-logger")
    # logger.setLevel(logging.INFO)
    # Fake reading the file.
    file = io.StringIO(FLASHCARD_PROGRAM)
    scan: Scanner = Scanner()
    current_line = file.readline()
    while current_line:
        scan.scan_tokens(current_line)
        # logger.info(result)
        current_line = file.readline()


def test_manic_program() -> None:
    """Scan the whole Manic program."""
    # logger: logging.Logger = logging.getLogger("test-logger")
    # logger.setLevel(logging.INFO)
    # Fake reading the file.
    file = io.StringIO(MANIC_PROGRAM)
    scan: Scanner = Scanner()
    current_line = file.readline()
    while current_line:
        scan.scan_tokens(current_line)
        # logger.info(result)
        current_line = file.readline()


def test_tictactoe_program() -> None:
    """Scan the whole Manic program."""
    # logger: logging.Logger = logging.getLogger("test-logger")
    # logger.setLevel(logging.INFO)
    # Fake reading the file.
    file = io.StringIO(TICTACTOE_PROGRAM)
    scan: Scanner = Scanner()
    current_line = file.readline()
    while current_line:
        scan.scan_tokens(current_line)
        # logger.info(result)
        current_line = file.readline()


def test_conditional_p_var() -> None:
    """Test 'IFX>PRETURN'."""
    scan: Scanner = Scanner()
    tokens = scan.scan_tokens("IFX>PRETURN")
    assert len(tokens) == 6
    assert tokens[0].tbp_type == TokenType.IF
    assert tokens[1].tbp_type == TokenType.IDENTIFIER
    assert tokens[2].tbp_type == TokenType.GREATER
    assert tokens[3].tbp_type == TokenType.IDENTIFIER
    assert tokens[4].tbp_type == TokenType.RETURN
