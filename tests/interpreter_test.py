"""Unit tests for the Interpreter class."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from typing import TYPE_CHECKING

from tbp.interpreter import Interpreter

# Ruff wants you to do 'import pytest', which you can see I did above, but
# that doesn't properly import CaptureFixture. Does anyone understand Python
# imports?
if TYPE_CHECKING:
    import pytest
    from pytest import CaptureFixture  # noqa: PT013


def test_initialization() -> None:
    """Test to see if the Interpreter initializes."""
    inter: Interpreter = Interpreter()
    assert inter is not None


def test_invalid_character() -> None:
    """Test '  %  '."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("  %  ")
    assert result is False


def test_print_no_params(capsys: CaptureFixture[str]) -> None:
    """Test 'PR'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("PR")
    output = capsys.readouterr()
    assert result is True
    assert output.out == "\n"


def test_print_string_param(capsys: CaptureFixture[str]) -> None:
    """Test 'PR "Pam!"'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line('PR "Pam!"')
    output = capsys.readouterr()
    assert result is True
    assert output.out == "Pam!\n"


def test_print_integer_param(capsys: CaptureFixture[str]) -> None:
    """Test 'PR 60'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("PR 60")
    output = capsys.readouterr()
    assert result is True
    assert output.out == "60\n"


def test_print_integer_comma_at_end(capsys: CaptureFixture[str]) -> None:
    """Test 'PR 60,'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("PR 60,")
    output = capsys.readouterr()
    assert result is True
    assert output.out == "60      "


def test_print_empty_string(capsys: CaptureFixture[str]) -> None:
    """Test 'PR ""'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line('PR ""')
    output = capsys.readouterr()
    assert result is True
    assert output.out == "\n"


def test_print_empty_string_in_middle(capsys: CaptureFixture[str]) -> None:
    """Test 'PR "X";"";"Y"'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line('PR "X";"";"Y"')
    output = capsys.readouterr()
    assert result is True
    assert output.out == "XY\n"


def test_store_prog_line(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 PR 60\n45 END'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("40 PR 60")
    result = inter.interpret_line("45 END")
    output = capsys.readouterr()
    assert result is True
    assert not output.out


def test_simple_list(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 PR "Pam!"\n45 END\nLIST'."""
    source: str = """
40 PR "Pam!"
45 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    result = inter.interpret_line("LIST")
    output = capsys.readouterr()
    assert result is True
    assert output.out == '40 PR "Pam!"\n45 END\n'


def test_list_single_line(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LIST 30'."""
    source: str = """
20 PR "Pam!"
30 PR "Charlie!"
40 PR "Sammy!"
50 PR "Harold!"
60 PR "Scout!"
70 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    result = inter.interpret_line("LIST 30")
    output = capsys.readouterr()
    assert result is True
    assert output.out == '30 PR "Charlie!"\n'


def test_list_single_line_show_rest(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LIST 31'."""
    source: str = """
20 PR "Pam!"
30 PR "Charlie!"
40 PR "Sammy!"
50 PR "Harold!"
60 PR "Scout!"
70 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    result = inter.interpret_line("LIST 31")
    output = capsys.readouterr()
    assert result is True
    assert (
        output.out
        == """40 PR "Sammy!"
50 PR "Harold!"
60 PR "Scout!"
70 END
"""
    )


def test_list_single_line_not_exist(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LIST 71'."""
    source: str = """
20 PR "Pam!"
30 PR "Charlie!"
40 PR "Sammy!"
50 PR "Harold!"
60 PR "Scout!"
70 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    result = inter.interpret_line("LIST 71")
    output = capsys.readouterr()
    assert result is True
    assert not output.out


def test_list_range(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LIST 31,49'."""
    source: str = """
20 PR "Pam!"
30 PR "Charlie!"
40 PR "Sammy!"
50 PR "Harold!"
60 PR "Scout!"
70 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    result = inter.interpret_line("LIST 31,49")
    output = capsys.readouterr()
    assert result is True
    assert output.out == '40 PR "Sammy!"\n'


def test_list_bad_param(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LIST 0'."""
    inter: Interpreter = Interpreter()
    result = inter.interpret_line("LIST 0")
    output = capsys.readouterr()
    assert result is False
    assert "Error #338: LIST parameters must be in the range 1 to 32767" in output.out


def test_list_reversed_params(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LIST 10,1'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line("LIST 10,1")
    output = capsys.readouterr()
    assert "Error #337: LIST parameters must be in logical order, not" in output.out


def test_run_no_program(capsys: CaptureFixture[str]) -> None:
    """Test 'RUN'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("RUN")
    output = capsys.readouterr()
    assert result is True
    assert output.out == "Error #013: No program in memory to run.\n"


def test_run_program(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 PR "Pam!"\n45 END\nRUN'."""
    source: str = """
40 PR "Pam!"
45 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    result = inter.interpret_line("RUN")
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_run_program_no_end(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 PR "Pam!"\n45 END\nRUN'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line('40 PR "Pam!"')
    assert result is True
    result = inter.interpret_line("RUN")
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\nError #335: No END in the program.\n"


def test_print_strings(capsys: CaptureFixture[str]) -> None:
    """Test numerous PRINT expressions."""

    def runit(inter: Interpreter, source: str, out_result: str) -> None:
        result: bool = inter.interpret_line(source)
        assert result is True
        output = capsys.readouterr()
        assert out_result in output.out

    source = """
10 let a=2
15 let b=6
20 let c=33
25 let q=157
30 let p=1293
35 let r=126
40 let i=8008
45 end
RUN
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    runit(inter, "print 1;2;3", "123")
    runit(inter, "print 4,5,6", "4       5       6")
    runit(inter, 'print "A=";A,"B+C="B+C', "A=2     B+C=39")


def test_list_comments(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 REM "Pam!"\n45 END\nLIST'."""
    source: str = """
40 REM "Pam!"
45 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    result = inter.interpret_line("LIST")
    output = capsys.readouterr()
    assert result is True
    assert output.out == '40 REM "Pam!"\n45 END\n'


def test_run_program_just_comments(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 REM "Pam!"\n45 END\nRUN'."""
    source: str = """
40 REM "Pam!"
45 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    result = inter.interpret_line("RUN")
    output = capsys.readouterr()
    assert result is True
    assert not output.out


def test_direct_assignment(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET A=100\nPR A'."""
    source: str = """
LET A=100
PRA
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "100\n"


def test_direct_assignment_no_let(capsys: CaptureFixture[str]) -> None:
    r"""Test 'a=100\nPR A'."""
    source: str = """
a=100
PRa
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "100\n"


def test_assignment_in_program(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 W=66\n45 END\nRUN\n"PRw'."""
    source: str = """
40 W=66
45 END
run
PRw
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "66\n"


def test_assignment_with_let_in_program(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET W=99\n45 END\nRUN\n"PRw'."""
    source: str = """
40 W=99
45 END
run
PRw
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "99\n"


def test_assignment_with_unary(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET W=96\n41 LET W=-W45 END\nRUN\n"PRw'."""
    source: str = """
40 W=96
41 B=-W
45 END
run
PRb
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "-96\n"


def test_assignment_with_unary_opposite(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET W=-96\n41 LET W=+W45 END\nRUN\n"PRw'."""
    source: str = """
40 W=-96
41 B=+W
45 END
run
PRb
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "96\n"


def test_assignment_with_basic_binary(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=2+2\nPRd'."""
    source: str = """
LET D=2+2
PRd
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "4\n"


def test_assignment_with_bigger_binary(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=2+2+3+3\nPRd'."""
    source: str = """
LET D=2+2+3+3
PRd
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "10\n"


def test_assignment_with_bad_binary(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=2+"G""'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line('LET D=2+"G"')
    output = capsys.readouterr()
    assert "Error #293: Syntax error - unexpected expression '\"G\"'" in output.out


def test_assignment_with_bad_binary_two(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D="G"+2"'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line('LET D="G"+2')
    output = capsys.readouterr()
    assert "Error #293: Syntax error - unexpected expression '\"G\"'" in output.out


def test_assignment_with_group(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=(2*2)+(3*3)\nPRd'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("LET D=(2*2)+(3*3)")
    assert result is True
    result = inter.interpret_line("PRd")
    assert result is True
    output = capsys.readouterr()
    assert output.out == "13\n"


def test_assignment_div_by_zero(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=10/0'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line("LET D=10/0")
    output = capsys.readouterr()
    assert "Division by zero" in output.out


def test_assignment_div_by_zero_from_var(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LETA=0\nLET D=10/A'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line("LETA=0")
    inter.interpret_line("LET D=10/A")
    output = capsys.readouterr()
    assert "Division by zero" in output.out


def test_assignment_big_expression(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=((((((((10/(3-1)))))))))\nPRd'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("LET D=((((((((10/(3-1)))))))))")
    result = inter.interpret_line("PRd")
    assert result is True
    output = capsys.readouterr()
    assert output.out == "5\n"


def test_assignment_rnd_expression(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=RND(10)'."""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_line("LET D=RND(10)")
    result = inter.interpret_line("PRd")
    assert result is True
    output = capsys.readouterr()
    assert len(output.out) > 0


def test_assignment_rnd_zero(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=RND(0)'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line("LET D=RND(0)")
    output = capsys.readouterr()
    assert "RND(0) not allowed" in output.out


def test_assignment_rnd_str(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=RND("A")'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line('LET D=RND("A")')
    output = capsys.readouterr()
    assert "Error #293: Syntax error - unexpected expression '\"A\"'" in output.out


def test_uninitialized_variable(capsys: CaptureFixture[str]) -> None:
    r"""Test 'LET D=A'."""
    inter: Interpreter = Interpreter()
    inter.interpret_line("LET D=A")
    output = capsys.readouterr()
    assert "Accessing uninitialized variable " in output.out


def test_block_with_error(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET W=96\n41 B=\nLET W=-W45 END\nRUN\n'."""
    source: str = """
40 W=96
41 B=
45 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is False
    output = capsys.readouterr()
    assert "Syntax Error: Error #023:" in output.out


def test_invalid_goto_line(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 GOTO 999\n41 END'."""
    source: str = """
40 GOTO 999
41 END
run
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "Error #046: GOTO subroutine does not exist '999'." in output.out


def test_goto(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 GOTO 45\n41 PRINT "Pam!"\n45 END\nrun\n'."""
    source: str = """
40 GOTO 45
41 PRINT "Pam!"
45 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert not output.out


def test_invalid_gosub_line(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 GOSUB 999\n41 END'."""
    source: str = """
40 GOSUB 999
41 END
run
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "Error #046: GOSUB subroutine does not exist '999'." in output.out


def test_gosub(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 gosub 45\n41 PRINT "Pam!"\n42 END\n45 return\nrun\n'."""
    source: str = """
40 gosub 45
41 PRINT "Pam!"
42 END
45 return
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_invalid_return(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 RETURN\n41 END'."""
    source: str = """
40 RETURN
41 END
run
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "Error #133: RETURN called with an empty call stack." in output.out


def test_gosub_last_statement(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 PRINT "Pam!\n41 GOSUB 45\n42 END\n45 GOSUB 42\nrun'."""
    source: str = """
40 PRINT "Pam!"
41 GOSUB 45
42 END
45 GOSUB 42
run
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "Error #345: GOSUB return address is invalid." in output.out


def test_if_equal(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET A=10\n41 if a=10 then PRINT "Pam!"\n42 END\nrun'."""
    source: str = """
40 LET A=10
41 if a=10 then PRINT "Pam!"
42 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_if_not_equal(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET A=11\n41 if a<>10 then PRINT "Pam!"\n42 END\nrun'."""
    source: str = """
40 LET A=11
41 if a<>10 then PRINT "Pam!"
42 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_if_less(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET A=10\n41 if a<11 then PRINT "Pam!"\n42 END\nrun'."""
    source: str = """
40 LET A=10
41 if a<11 then PRINT "Pam!"
42 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_if_less_equal(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET A=10\n41 if a<=11 then PRINT "Pam!"\n42 END\nrun'."""
    source: str = """
40 LET A=10
41 if a<=11 then PRINT "Pam!"
42 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_if_greater(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET A=20\n41 if a>11 then PRINT "Pam!"\n42 END\nrun'."""
    source: str = """
40 LET A=20
41 if a>11 then PRINT "Pam!"
42 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_if_greater_equal(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET A=11\n41 if a>=11 then PRINT "Pam!"\n42 END\nrun'."""
    source: str = """
40 LET A=11
41 if a>=11 then PRINT "Pam!"
42 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert output.out == "Pam!\n"


def test_if_no_branch(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 LET A=10\n41 if a>=11 then PRINT "Pam!"\n42 END\nrun'."""
    source: str = """
40 LET A=10
41 if a>=11 then PRINT "Pam!"
42 END
run
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert not output.out


def test_clear_direct_exec(capsys: CaptureFixture[str]) -> None:
    r"""Test 'CLEAR'."""
    source: str = """
ClEaR
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert not output.out


def test_clear_program_line(capsys: CaptureFixture[str]) -> None:
    r"""Test '40 CLEAR\n41 END\nrun'."""
    source: str = """
40 ClEaR
41 eNd
rUn
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    assert result is True
    output = capsys.readouterr()
    assert not output.out


def test_delete_program_line(capsys: CaptureFixture[str]) -> None:
    r"""Test '40^LIST'."""
    source: str = """
20 PR "AAA!"
30 PR "BBB"
40 PR "CCC"
50 PR "DDD"
60 PR "EEE"
70 END
"""
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    result = inter.interpret_line("40")
    assert result is True
    result = inter.interpret_line("LIST")
    output = capsys.readouterr()
    assert result is True
    assert ("CCC" in output.out) is False


def test_delete_unknown_program_line(capsys: CaptureFixture[str]) -> None:
    r"""Test '40^LIST'."""
    source: str = """
20 PR "AAA!"
30 PR "BBB"
40 PR "CCC"
50 PR "DDD"
60 PR "EEE"
70 END
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    inter.interpret_line("22")
    output = capsys.readouterr()
    assert "Error #347: Line number is not in the program: '22'" in output.out


def test_simple_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'INPUT a'."""
    source = """10 INPUT a
20 PRINT "A=";A
30 END
RUN
"""
    cmds = iter(["11", "%q"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert result is True
    assert "A=11" in output.out


def test_simple_multiple_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'INPUT a,b'."""
    source = """10 INPUT a,b
20 PRINT "A=";A
21 PRINT "B=";B
30 END
RUN
"""
    cmds = iter(["11,22", "%q"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert result is True
    assert "A=11" in output.out
    assert "B=22" in output.out


def test_simple_multiple_individual_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'INPUT a,b'."""
    source = """10 INPUT a,b
20 PRINT "A=";A
21 PRINT "B=";B
30 END
RUN
"""
    cmds = iter(["11", "22", "%q"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert result is True
    assert "A=11" in output.out
    assert "B=22" in output.out


def test_invalid_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'INPUT a'."""
    source = """10 INPUT a
20 PRINT "A=";A
30 END
RUN
"""
    cmds = iter(["xyzzy", "%q"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert result is True
    assert "Invalid value in INPUT: 'xyzzy'." in output.out
    assert "Setting 'A=0' as default." in output.out


def test_too_much_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'INPUT a'."""
    source = """10 INPUT a
20 PRINT "A=";A
30 END
RUN
"""
    cmds = iter(["10,20", "%q"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert result is True
    assert (
        "WARN #001: More input given than variables requested by INPUT." in output.out
    )


def test_run_param_to_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'RUN 99'."""
    source = """10 INPUT a
20 PRINT "A=";A
30 END
RUN 99
"""
    cmds = iter(["\n", "%q"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert result is True
    assert "A=99" in output.out


def test_run_invalid_param_to_input(
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test 'RUN C'."""
    source = """10 INPUT a
20 PRINT "A=";A
30 END
RUN C
"""
    cmds = iter(["\n", "%q"])
    monkeypatch.setattr("builtins.input", lambda _: next(cmds))
    inter: Interpreter = Interpreter()
    result: bool = inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert result is True
    assert "Error #336: Accessing uninitialized variable 'C'." in output.out


def test_invalid_usr_routine(capsys: CaptureFixture[str]) -> None:
    r"""Test 'USR(100)'."""
    source: str = "USR(100)"
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert (
        "Error #360: USR only supports read (276) or write (280) subroutines, given 100"
        in output.out
    )


def test_invalid_usr_xreg(capsys: CaptureFixture[str]) -> None:
    r"""Test 'USR(100)'."""
    source: str = "USR(S+20)"
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert (
        "Error #361: USR read/write routines require an address in XReg." in output.out
    )


def test_invalid_usr_areg(capsys: CaptureFixture[str]) -> None:
    r"""Test 'USR(100)'."""
    source: str = "USR(S+24,100)"
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "Error #362: USR write routine requires a value in AReg." in output.out


def test_usr_write(capsys: CaptureFixture[str]) -> None:
    r"""Test USR writing and return."""
    source: str = """LET N=USR(S+24,100,13)
LET N=USR(S+24,100,99)
PR "n=";n
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "n=99" in output.out


def test_usr_write_read(capsys: CaptureFixture[str]) -> None:
    r"""Test USR writing and reading."""
    source: str = """USR(S+24,100,99)
LET N=USR(S+20,100)
PRINT "n=";N
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "n=99" in output.out


def test_usr__read_write_neg_address(capsys: CaptureFixture[str]) -> None:
    r"""Test USR reading and writing negative addresses."""
    source: str = """USR(S+24,-100,11)
LET N=USR(S+20,-100)
PRINT "n=";N"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "n=11" in output.out


def test_usr_read_initialization(capsys: CaptureFixture[str]) -> None:
    r"""Test USR reading initialization."""
    source: str = """N=USR(S+20,100)
PR "n=";N
"""
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert "n=0" in output.out


def test_invalid_byte_to_write(capsys: CaptureFixture[str]) -> None:
    r"""Test USR writing outside 0-256."""
    source: str = "LET P=USR(S+24, 100, 299)"
    inter: Interpreter = Interpreter()
    inter.interpret_buffer(source)
    output = capsys.readouterr()
    assert (
        "Error #362: USR write routine on supports values in AReg between 0 "
        "and 256, given '299'." in output.out
    )
