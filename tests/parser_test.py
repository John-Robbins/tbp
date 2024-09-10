"""Unit tests for the Parser class."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING, cast

import pytest

from tbp.astprinter import AstPrinter
from tbp.errors import TbpSyntaxError
from tbp.languageitems import (
    LineNumber,
    Literal,
    Print,
)
from tbp.parser import Parser
from tbp.scanner import Scanner
from tests.programs import FLASHCARD_PROGRAM, MANIC_PROGRAM, TICTACTOE_PROGRAM

if TYPE_CHECKING:
    from pytest import CaptureFixture  # noqa: PT013

    from tbp.languageitems import (
        LanguageItem,
    )
    from tbp.tokens import Token


def test_initialization() -> None:
    """Test to see if the parser initializes."""
    scan: Parser = Parser()
    assert scan is not None


def test_single_print_statement() -> None:
    """Parse a single print statement."""
    scan: Scanner = Scanner()
    source: str = "print"
    tokens: list[Token] = scan.scan_tokens(source)
    parse: Parser = Parser()
    stmts: list[LanguageItem] = parse.parse_tokens(tokens)
    assert len(stmts) == 1
    assert type(stmts[0]).__qualname__ == "Print"


def test_print_line_statement() -> None:
    """Parse a single print statement."""
    scan: Scanner = Scanner()
    source: str = "111 print 999"
    tokens: list[Token] = scan.scan_tokens(source)
    parse: Parser = Parser()
    stmts: list[LanguageItem] = parse.parse_tokens(tokens)
    assert len(stmts) == 2
    num: LineNumber = cast(LineNumber, stmts[0])
    assert num.value == 111
    stmt: Print = cast(Print, stmts[1])
    expr: Literal = cast(Literal, stmt.expressions[0])
    assert expr.value == 999


def test_basic_print() -> None:
    """The basics of the ast printer."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("111 print 999")
    assert result == "[Line# 111][PRINT (999)]"


def test_print_and_string() -> None:
    """The basics of the ast printer."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print('111 print "Pam!"')
    assert result == '[Line# 111][PRINT ("Pam!")]'


def test_print_no_line_number() -> None:
    """The basics of the ast printer."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print('print "Pam!"')
    assert result == '[PRINT ("Pam!")]'


def test_print_separators() -> None:
    """The printer separators."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print('print "Pam!",10;"Pearl"')
    assert result == '[PRINT ("Pam!", [,], 10, [;], "Pearl")]'


def test_print_colon_end() -> None:
    """The printer colon at the end.."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print('print "Pam!":')
    # NOTE! The colon is eaten during parsing since we don't use it.
    assert result == '[PRINT ("Pam!")]'


def test_print_error_with_separators() -> None:
    """The printer error with separators on the front."""
    thing: AstPrinter = AstPrinter()
    error_test: str = (
        "Separators or colons cannot be the first item in a PRINT statement."
    )
    with pytest.raises(TbpSyntaxError, match=error_test):
        thing.print('print ,"Pam!",10;"Pearl"')


def test_print_error_with_colon() -> None:
    """The printer error with a colon in the middle."""
    thing: AstPrinter = AstPrinter()
    error_test: str = "Expected the end of the line but found ','"
    with pytest.raises(TbpSyntaxError, match=error_test):
        thing.print('print "Pam!":,10;"Pearl"')


def test_invalid_line_number() -> None:
    """Test invalid line numbers."""
    thing: AstPrinter = AstPrinter()
    error: str = (
        "Syntax Error: [Ln 0, Col 2] (Error #009: Line number '0' not allowed.)"
    )
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print('0 PRINT "PAM!"')
    assert error in str(exec_info.value)


def test_invalid_line_number_big_num() -> None:
    """Test invalid big line numbers."""
    thing: AstPrinter = AstPrinter()
    error: str = (
        "Syntax Error: [Ln 65536, Col 6] (Error #009: Line number '65536' not allowed.)"
    )
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print('65536 PRINT "PAM!"')
    assert error in str(exec_info.value)


def test_rem_statements() -> None:
    """Test comments."""

    def runit(source: str) -> str:
        thing: AstPrinter = AstPrinter()
        return thing.print(source)

    result = runit("REM %^&$#@!")
    assert result == "[REM %^&$#@!]"
    result = runit("111 REM %^&$#@!")
    assert result == "[Line# 111][REM %^&$#@!]"


def test_simple_let() -> None:
    """Try a correct LET."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("111 LET A=99")
    assert result == "[Line# 111][LET [Var A] = 99]"


def test_let_error_no_variable() -> None:
    """Test assignments with errors."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError):
        thing.print("LET")


def test_let_error_wrong_variable() -> None:
    """Test assignments with errors."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("LET 1")
    assert "but found '1'" in str(exec_info.value)


def test_let_error_no_equal() -> None:
    """Test assignments with errors."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("LET A")
    assert "Error #020: LET is missing" in str(exec_info.value)


def test_let_error_no_expression() -> None:
    """Test assignments with errors."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError):
        thing.print("LET A=")


def test_simple_silent_let() -> None:
    """Try a correct LET without the LET."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("111 A=99")
    assert result == "[Line# 111][LET [Var A] = 99]"


def test_simple_addition_expression() -> None:
    """Try 'PRINT 1+1'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT 1+1")
    assert result == "[PRINT ([+ 1, 1])]"


def test_group_multiplication_expression() -> None:
    """Try 'PRINT (A+B)*10'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT (A+B)*10")
    assert result == "[PRINT ([* [Group [+ [Var A], [Var B]]], 10])]"


def test_simple_unary_expression() -> None:
    """Try 'PRINT -a'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT -a")
    assert result == "[PRINT ([Unary - [Var a]])]"


def test_error_multiple_stars() -> None:
    """Try 'PRINT A**B'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("PRINT A**B")
    assert "Error #293: Syntax error" in str(exec_info.value)


def test_big_expression() -> None:
    """Try 'PRINT (A+B+C)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT (A+B+C)")
    assert result == "[PRINT ([Group [+ [+ [Var A], [Var B]], [Var C]]])]"


def test_even_bigger_expression() -> None:
    """Try 'PRINT (A+B+C)/(-A)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT (A+B+C)/(-A)")
    assert result == (
        "[PRINT ([/ [Group [+ [+ [Var A], [Var B]], [Var C]]], "
        "[Group [Unary - [Var A]]]])]"
    )


def test_crazy_expression() -> None:
    """Try 'PRINT (A+B+C)/(-A)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT -(A+B+C)*((-A/B)+C)")
    assert result == (
        "[PRINT ([* [Unary - [Group [+ [+ [Var A], [Var B]], [Var C]]]], "
        "[Group [+ [Group [/ [Unary - [Var A]], [Var B]]], [Var C]]]])]"
    )


def test_crazy_multiplication_expression() -> None:
    """Try 'PRINT -(A*B*C)/(+A)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT -(A*B*C)*((-X/Y)+Z)")
    assert result == (
        "[PRINT ([* [Unary - [Group [* [* [Var A], [Var B]], [Var C]]]], "
        "[Group [+ [Group [/ [Unary - [Var X]], [Var Y]]], [Var Z]]]])]"
    )


def test_crazy_grouping_expression() -> None:
    """Try 'PRINT -(+(-(+(-(A*222)))))'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("PRINT -(+(-(+(-(A*222)))))")
    assert result == (
        "[PRINT ([Unary - [Group [Unary + [Group [Unary - [Group [Unary + "
        "[Group [Unary - [Group [* [Var A], 222]]]]]]]]]]])]"
    )


def test_print_trailing_semicolon() -> None:
    """Test: '80 PRINT "LEVEL OF DIFFICULTY";'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print('80 PRINT "LEVEL OF DIFFICULTY";')
    assert result == ('[Line# 80][PRINT ("LEVEL OF DIFFICULTY", [;])]')


def test_simple_goto() -> None:
    """Test 'GOTO 111'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("GOTO 111")
    assert result == "[GOTO 111]"


def test_simple_gosub() -> None:
    """Test 'GOSUB 111'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("GOSUB 111")
    assert result == "[GOSUB 111]"


def test_missing_goto_expression() -> None:
    """Test a GOTO missing the expression."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("GOTO")
    assert "Error #037: Missing line " in str(exec_info.value)


def test_simple_return() -> None:
    """Test 'Return'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("Return")
    assert result == "[RETURN]"


def test_simple_end() -> None:
    """Test 'End'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("End")
    assert result == "[END]"


def test_simple_list() -> None:
    """Test 'LIST'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("list")
    assert result == "[LIST None, None]"


def test_simple_list_one_param() -> None:
    """Test 'LIST 111'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("list 111")
    assert result == "[LIST 111, None]"


def test_simple_list_two_param() -> None:
    """Test 'LIST 111, 999'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("list 111, 999")
    assert result == "[LIST 111, 999]"


def test_stuff_after_statement() -> None:
    """Test 'LIST 100,200 RETURN'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("LIST 100,200 RETURN")
    assert "Expected the end of the line but found 'RETURN'." in str(exec_info.value)


def test_simple_if() -> None:
    """Test 'IF I>25 THEN PRINT "ERROR"'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print('IF I>25 THEN PRINT "ERROR"')
    assert result == '[IF ([Var I] [>] 25) [THEN [PRINT ("ERROR")]]]'


def test_if_no_then() -> None:
    """Test 'IF N/P*P>N GOTO 100'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("IF N/P*P>N GOTO 100")
    assert (
        result
        == "[IF ([* [/ [Var N], [Var P]], [Var P]] [>] [Var N]) [THEN [GOTO 100]]]"
    )


def test_if_equal_no_then() -> None:
    """Test 'IF N/P*P=N GOTO 100'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("IF N/P*P=N GOTO 100")
    assert (
        result
        == "[IF ([* [/ [Var N], [Var P]], [Var P]] [=] [Var N]) [THEN [GOTO 100]]]"
    )


def test_if_nest_if() -> None:
    """Test 'IF X+T > 50 THEN IF I <> J PRINT Q,R'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("IF X+T > 50 THEN IF I <> J PRINT Q,R")
    assert result == (
        "[IF ([+ [Var X], [Var T]] [>] 50) [THEN [IF ([Var I] [<>] [Var J])"
        " [THEN [PRINT ([Var Q], [,], [Var R])]]]]]"
    )


def test_empty_if() -> None:
    """Test 'IF'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("IF")
    assert "Error #293: Syntax error " in str(exec_info.value)


def test_if_missing_parts() -> None:
    """Test IF with various missing pieces."""

    def runit(source: str, error: str) -> None:
        thing: AstPrinter = AstPrinter()
        with pytest.raises(TbpSyntaxError) as exec_info:
            thing.print(source)
        assert error in str(exec_info.value)

    runit("IF", "Error #293:")
    runit("IF A", "Error #330:")
    runit("IF A=", "Error #293:")
    runit("IF A=B", "Error #293:")
    runit("IF A=B THEN", "Error #293:")


def test_if_space_goto() -> None:
    """Test '240 IF M<3 THEN GO TO 220'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("240 IF M<3 THEN GO TO 220")
    assert result == "[Line# 240][IF ([Var M] [<] 3) [THEN [GOTO 220]]]"


def test_simple_clear() -> None:
    """Test 'Clear'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("clear")
    assert result == "[CLEAR]"


def test_simple_input() -> None:
    """Test 'INPUT A'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("INPUT A")
    assert result == "[INPUT ([Var A])]"


def test_input_five_vars() -> None:
    """Test 'INPUT A,B,   C, D,    E'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("INPUT A,B,   C, D,    E")
    assert result == "[INPUT ([Var A], [Var B], [Var C], [Var D], [Var E])]"


def test_input_missing_parts() -> None:
    """Test INPUT with missing parts."""

    def runit(source: str, error: str) -> None:
        thing: AstPrinter = AstPrinter()
        with pytest.raises(TbpSyntaxError) as exec_info:
            thing.print(source)
        assert error in str(exec_info.value)

    runit("INPUT", "Error #104: INPUT expected")
    runit("INPUT 6", "Error #104: INPUT expected")
    runit("INPUT A,", "Error #104: INPUT expected")
    runit("INPUT A,5", "Error #104: INPUT expected")


def test_simple_run() -> None:
    """Test 'RUN'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("run")
    assert result == "[RUN]"


def test_run_on_line() -> None:
    """Test '100 RUN'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("100 run")
    assert result == "[Line# 100][RUN]"


def test_run_on_line_with_params() -> None:
    """Test '100 RUN A,B,C'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("100 RUN A,B,C")
    assert result == "[Line# 100][RUN]"


def test_run_with_args() -> None:
    """Test 'RUN A,B'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("RUN A,B")
    assert result == "[RUN ([Var A], [Var B])]"


def test_run_with_comma_before_args() -> None:
    """Test 'RUN,A,B'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("RUN,A,B")
    assert result == "[RUN ([Var A], [Var B])]"


def test_run_with_trailing_comma() -> None:
    """Test 'RUN,A,B,'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("RUN,A,B,")
    assert "Error #296: Syntax error" in str(exec_info.value)


def test_simple_random() -> None:
    """Test '100 LET A=RND(100)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("100 LET A=RND(100)")
    assert result == "[Line# 100][LET [Var A] = [RND(100)]]"


def test_random_with_missing_left() -> None:
    """Test '100 LET A=RND 100)'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("100 LET A=RND 100)")
    assert "Error #293: Syntax error " in str(exec_info.value)


def test_random_with_missing_right() -> None:
    """Test '100 LET A=RND (100'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("100 LET A=RND (100")
    assert "Error #293: Syntax error " in str(exec_info.value)


def test_simple_usr() -> None:
    """Test '100 LET A=USR(100)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("100 LET A=USR(100)")
    assert result == "[Line# 100][LET [Var A] = [USR(100)]]"


def test_simple_two_param_usr() -> None:
    """Test '100 LET A=USR(100,999)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("100 LET A=USR(100,999)")
    assert result == "[Line# 100][LET [Var A] = [USR(100, 999)]]"


def test_simple_three_param_usr() -> None:
    """Test '100 LET A=USR(111,222,333)'."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("100 LET A=USR(111,222,333)")
    assert result == "[Line# 100][LET [Var A] = [USR(111, 222, 333)]]"


def test_usr_with_missing_left() -> None:
    """Test '100 LET A=USR 100)'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("100 LET A=USR 100)")
    assert "Error #293: Syntax error " in str(exec_info.value)


def test_usr_with_missing_right() -> None:
    """Test '100 LET A=USR(100'."""
    thing: AstPrinter = AstPrinter()
    with pytest.raises(TbpSyntaxError) as exec_info:
        thing.print("100 LET A=USR(100")
    assert "Error #293: Syntax error " in str(exec_info.value)


def test_flashcard_program() -> None:
    """Test using the flashcard program."""
    logger: logging.Logger = logging.getLogger("test-logger")
    # logger.setLevel(logging.INFO)
    # Fake reading the file.
    file = io.StringIO(FLASHCARD_PROGRAM)
    thing: AstPrinter = AstPrinter()
    current_line = file.readline()
    while current_line:
        result: str = thing.print(current_line)
        logger.info(result)
        current_line = file.readline()


def test_manic_program() -> None:
    """Test using the flashcard program."""
    logger: logging.Logger = logging.getLogger("test-logger")
    # logger.setLevel(logging.INFO)
    # Fake reading the file.
    file = io.StringIO(MANIC_PROGRAM)
    thing: AstPrinter = AstPrinter()
    current_line = file.readline()
    while current_line:
        result: str = thing.print(current_line)
        logger.info(result)
        current_line = file.readline()


def test_tictactoe_program() -> None:
    """Test using the flashcard program."""
    logger: logging.Logger = logging.getLogger("test-logger")
    # logger.setLevel(logging.INFO)
    # Fake reading the file.
    file = io.StringIO(TICTACTOE_PROGRAM)
    thing: AstPrinter = AstPrinter()
    current_line = file.readline()
    while current_line:
        result: str = thing.print(current_line)
        logger.info(result)
        current_line = file.readline()


def test_commands_quit(
    capsys: CaptureFixture[str],
) -> None:
    """Test `tbp -c stuff'."""
    scan: Scanner = Scanner()
    source: str = "111 RUN a,10,c"
    tokens: list[Token] = scan.scan_tokens(source)
    parse: Parser = Parser()
    stmts: list[LanguageItem] = parse.parse_tokens(tokens)
    output = capsys.readouterr()
    assert len(stmts) == 2
    assert (
        "WARN #002: RUN parameters not supported in programs, only in "
        "direct execution: Line [111]"
    ) in output.out


def test_simple_let_less_assignment() -> None:
    """Try a correct LET."""
    thing: AstPrinter = AstPrinter()
    result: str = thing.print("111 A=99")
    assert result == "[Line# 111][LET [Var A] = 99]"
