"""The Abstract Syntax Tree printer."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tbp.languageitems import (
    LanguageItem,
    PrintSeparator,
    Visitor,
)
from tbp.parser import Parser
from tbp.scanner import Scanner

if TYPE_CHECKING:
    from tbp.languageitems import (
        Assignment,
        Binary,
        Clear,
        End,
        Gosub,
        Goto,
        Group,
        If,
        Input,
        Let,
        LineNumber,
        List,
        Literal,
        Print,
        Random,
        RemComment,
        Return,
        Run,
        String,
        Unary,
        Usr,
        Variable,
    )
    from tbp.tokens import Token


class AstPrinter(Visitor):
    """
    A simple abstract syntax tree printer.

    This class used to help test the parser and for diagnostic logging in the
    Interpreter class. Seeing the parsed values as text is so helpful for
    debugging and testing. Yet another great idea from Robert Nystrom.
    """

    def __init__(self: AstPrinter) -> None:
        """Initialize the AstPrinter class."""
        self._scanner: Scanner = Scanner()
        self._parser: Parser = Parser()
        self._builder: str = ""
        # The common return. All returns are ignored by this visitor, but all
        # those visit methods need to return something to keep Python happy.
        self._common_return: PrintSeparator = PrintSeparator(0, 0, "!")

    def print(self: AstPrinter, source: str | list[LanguageItem]) -> str:
        """Return a representative string for the Tiny BASIC code."""
        self._builder = ""
        program: list[LanguageItem]
        if isinstance(source, str):
            tokens: list[Token] = self._scanner.scan_tokens(source)
            program = self._parser.parse_tokens(tokens)
        else:
            program = source

        for item in program:
            item.accept(self)

        return self._builder

    def _add_to_buffer(self: AstPrinter, to_add: str) -> None:
        self._builder += to_add

    def visit_linenumber_statement(
        self: AstPrinter,
        expression: LineNumber,
    ) -> LanguageItem:
        """Process a line number statement."""
        self._put_brackets("Line#", expression.value)
        return self._common_return

    def visit_print_statement(self: AstPrinter, expression: Print) -> LanguageItem:
        """Process a PRINT statement."""
        self._put_brackets("PRINT", expression.expressions)
        return self._common_return

    def visit_print_separator_statement(
        self: AstPrinter,
        expression: PrintSeparator,
    ) -> LanguageItem:
        """Process a print separator."""
        self._add_to_buffer(f"[{expression.separator}]")
        return self._common_return

    def visit_literal_expression(
        self: AstPrinter,
        expression: Literal,
    ) -> LanguageItem:
        """Process a hard coded number."""
        self._add_to_buffer(str(expression.value))
        return self._common_return

    def visit_string_expression(self: AstPrinter, expression: String) -> LanguageItem:
        """Process a string."""
        self._add_to_buffer(f'"{expression.value}"')
        return self._common_return

    def visit_rem_statement(
        self: AstPrinter,
        expression: RemComment,
    ) -> LanguageItem:
        """Process a comment."""
        # Yes, there is no space between REM and the comment. The scanner
        # hovers up everything after the 'M' to the end of the string.
        self._add_to_buffer(f"[REM{expression.value}]")
        return self._common_return

    def visit_let_statement(self: AstPrinter, expression: Let) -> LanguageItem:
        """Process an assignment."""
        self._put_brackets("LET", expression.assign)
        return self._common_return

    def visit_assignment_expression(
        self: AstPrinter,
        expression: Assignment,
    ) -> LanguageItem:
        """Process an assignment."""
        # Have the variable do its thing.
        expression.variable.accept(self)
        self._add_to_buffer(" = ")
        expression.expression.accept(self)
        return self._common_return

    def visit_variable_expression(
        self: AstPrinter,
        variable: Variable,
    ) -> LanguageItem:
        """Process a variable."""
        self._add_to_buffer(f"[Var {variable.name}]")
        return self._common_return

    def visit_unary_expression(self: AstPrinter, unary: Unary) -> LanguageItem:
        """Process a unary expression."""
        self._put_brackets(f"Unary {unary.operator.lexeme}", unary.expression)
        return self._common_return

    def visit_binary_expression(self: AstPrinter, binary: Binary) -> LanguageItem:
        """Process a binary expression."""
        self._put_brackets(binary.operator.lexeme, binary.lhs, binary.rhs)
        return self._common_return

    def visit_group_expression(self: AstPrinter, group: Group) -> LanguageItem:
        """Process a group expression."""
        self._put_brackets("Group", group.expression)
        return self._common_return

    def visit_random_expression(self: AstPrinter, random: Random) -> LanguageItem:
        """Process a RND expression."""
        self._add_to_buffer("[RND(")
        self._process_pieces(random.expression)
        self._add_to_buffer(")]")
        return self._common_return

    def visit_usr_expression(self: AstPrinter, usr: Usr) -> LanguageItem:
        """Process a USR expression."""
        self._add_to_buffer("[USR(")
        self._process_pieces(usr.subroutine)
        if usr.x_reg is not None:
            self._add_to_buffer(", ")
            self._process_pieces(usr.x_reg)
        if usr.a_reg is not None:
            self._add_to_buffer(", ")
            self._process_pieces(usr.a_reg)
        self._add_to_buffer(")]")
        return self._common_return

    def visit_goto_statement(self: AstPrinter, goto: Goto) -> LanguageItem:
        """Process a GOTO statement."""
        self._put_brackets("GOTO", goto.target)
        return self._common_return

    def visit_gosub_statement(self: AstPrinter, gosub: Gosub) -> LanguageItem:
        """Process a GOSUB statement."""
        self._put_brackets("GOSUB", gosub.target)
        return self._common_return

    def visit_return_statement(self: AstPrinter, ret: Return) -> LanguageItem:
        """Process a RETURN statement."""
        del ret
        self._add_to_buffer("[RETURN]")
        return self._common_return

    def visit_end_statement(self: AstPrinter, end: End) -> LanguageItem:
        """Process an END statement."""
        del end
        self._add_to_buffer("[END]")
        return self._common_return

    def visit_list_statement(self: AstPrinter, lister: List) -> LanguageItem:
        """Process a LIST statement."""
        self._put_brackets("LIST", lister.start_line, lister.end_line)
        return self._common_return

    def visit_if_statement(self: AstPrinter, if_stmt: If) -> LanguageItem:
        """Process an IF statement."""
        self._add_to_buffer("[IF (")
        self._process_pieces(if_stmt.lhs)
        self._add_to_buffer(f" [{if_stmt.operator.lexeme}] ")
        self._process_pieces(if_stmt.rhs)
        self._add_to_buffer(") [THEN ")
        self._process_pieces(if_stmt.branch)
        self._add_to_buffer("]]")

        return self._common_return

    def visit_clear_statement(self: AstPrinter, clear: Clear) -> LanguageItem:
        """Process a CLEAR statement."""
        del clear
        self._add_to_buffer("[CLEAR]")
        return self._common_return

    def visit_input_statement(self: AstPrinter, input_stmt: Input) -> LanguageItem:
        """Process an INPUT statement."""
        self._put_brackets("INPUT", input_stmt.variables)
        return self._common_return

    def visit_run_statement(self: AstPrinter, run_stmt: Run) -> LanguageItem:
        """Process a RUN statement."""
        if len(run_stmt.input_values) > 0:
            self._put_brackets("RUN", run_stmt.input_values)
        else:
            self._add_to_buffer("[RUN]")
        return self._common_return

    ###########################################################################
    # Internal implementation methods.
    ###########################################################################

    SupportedTypes = LanguageItem | int | str | None

    # The ANN401 warning below is valid, but for this test only code, it sure
    # makes life a lot easier.
    # https://docs.astral.sh/ruff/rules/any-type/
    def _put_brackets(
        self: AstPrinter,
        name: str,
        *pieces: Any,  # noqa: ANN401
    ) -> None:
        """Put appropriate brackets around things."""
        self._add_to_buffer(f"[{name} ")
        self._process_pieces(*pieces)
        self._add_to_buffer("]")

    def _process_pieces(
        self: AstPrinter,
        *args: SupportedTypes | list[SupportedTypes],
    ) -> None:
        """Add sub parts to the bracketed string."""
        args_len: int = len(args)
        for curr_arg, piece in enumerate(args):
            if isinstance(piece, LanguageItem):
                piece.accept(self)
            elif isinstance(piece, list):
                if (length := len(piece)) > 0:
                    self._add_to_buffer("(")
                    for i, item in enumerate(piece):
                        # Captain Recursion!
                        self._process_pieces(item)
                        if i < (length - 1):
                            self._add_to_buffer(", ")
                    self._add_to_buffer(")")
                else:
                    self._add_to_buffer("())")
            else:
                self._add_to_buffer(str(piece))
            if curr_arg < args_len - 1:
                self._add_to_buffer(", ")
