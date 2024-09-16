"""The Tiny BASIC linter."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sortedcontainers import SortedDict, SortedList

from tbp.helpers import build_error_string, print_output
from tbp.languageitems import (
    Literal,
    PrintSeparator,
    Visitor,
)

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
        LanguageItem,
        Let,
        LineNumber,
        List,
        Print,
        ProgramLine,
        Random,
        RemComment,
        Return,
        Run,
        String,
        Unary,
        Usr,
        Variable,
    )

# As this is a linter, primarily looking for uninitialized variables, it's not
# a full interpreter. Hence, there's various visit* methods that I'll never
# use, such as visit_print_separator. Since they are never called in most
# cases, I've applied # pragma: no cover to those methods so I don't have to
# create pointless unit test cases.


class Linter(Visitor):
    """
    Lints parsed Tiny BASIC code and looks for common mistakes.

    This is not the world's most amazing linter. I made it because I kept
    screwing up GOTO and GOSUB hard coded addresses and wanted a sanity check
    to avoid dumb mistakes. Since END and CLEAR checking were simple, I threw
    those in.

    When I decided to do the uninitialized variable checking, my original
    thought was to do something relatively quick. The idea was to start at the
    first line of the program and do the following going down the program:

        A) If I saw a variable being initialized by LET (assignment) or INPUT,
        store it in an initialized list.
        B) If I saw a variable being used, and it was in the initialized list,
        it was good.
        C) If the variable wasn't in the initialized list, I put it in a
        potentially uninitialized list.
        D) At the end of the linting, I'd remove any potentially uninitialized
        variables that were in the final initialized list.
        E) Any items left in the potentially uninitialized list were reported.

    That's not the smartest algorithm, but sufficient to find dumb mistakes but
    not have a lot of false positives.

    Pondering a little more, I thought maybe it would be good to skip step D)
    as maybe there are cases where there were branches at the beginning that
    jumped down to far away locations, did the initialization there, and jumped
    back. The earlier parts of the program are using the variables, but what if
    they didn't get properly initialized? That's what I called "strict" mode
    here.

    The next step would be to start analyzing execution flow through the
    program. That's definitely doable and something I want to explore in the
    future. However, the reality is that even three people out of eight billion
    in the world actually downloading and trying tbp has fewer odds than me
    spontaneously turning into an apple.

    """

    @dataclass
    class ErrorItem:
        """Holds a single error."""

        # The line number.
        line: int
        # The error message
        msg: str

    def __init__(self: Linter) -> None:
        """Initialize the Linter class."""
        # The linter doesn't need return values on a lot of the statements so
        # this is a return value to use so we keep Python happy.
        self._common_return: PrintSeparator = PrintSeparator(0, 0, "!")

        # The program lines.
        self._lines: SortedDict[int, ProgramLine]

        # The current line being processed.
        self._curr_line: ProgramLine

        # The list of initialized variables.
        self._initialized_vars: SortedList[str] = SortedList()

        # The flag that checks if we have an END statement in the program.
        self._had_end_statement: bool = False

        # The list of errors.
        self._errorlist: SortedList[Linter.ErrorItem] = SortedList(key=lambda x: x.line)

        # The potential errors dictionary.
        self._potential_errors: SortedDict[str, list[Linter.ErrorItem]] = SortedDict()

    # https://docs.astral.sh/ruff/rules/boolean-type-hint-positional-argument/
    # https://docs.astral.sh/ruff/rules/boolean-default-value-positional-argument/
    # This is a good rule, but in this small case, here it would be more
    # trouble than it's worth to go with string literals or separate methods.
    def lint_program(
        self: Linter,
        program: SortedDict[int, ProgramLine],
        strict: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        """Lints the program."""
        self._lines = program

        # Run through the program.
        for line in self._lines:
            self._curr_line = self._lines[line]
            self._curr_line.data[1].accept(self)

        # Did we find an END?
        if self._had_end_statement is False:
            # self._errors.append("LINT #01: Missing END statement in the program.\n")
            self._errorlist.add(
                Linter.ErrorItem(
                    32767,
                    "LINT #01: Missing END statement in the program.",
                ),
            )

        if strict is False:
            # Remove any potentially uninitialized errors that might have been
            # initialized by a different path.
            for var in self._initialized_vars:
                self._potential_errors.pop(var, None)

        # Add the potentially uninitialized to the error list.
        for item in self._potential_errors:
            for error in self._potential_errors[item]:
                self._errorlist.add(error)

        # Finally, report all the errors.
        for error in self._errorlist:
            print_output(f"{error.msg}\n")

    def visit_linenumber_statement(
        self: Linter,
        expression: LineNumber,
    ) -> LanguageItem:
        """Process a line number statement."""
        del expression  # pragma: no cover
        return self._common_return  # pragma: no cover

    def visit_print_statement(self: Linter, expression: Print) -> LanguageItem:
        """Process a PRINT statement."""
        for arg in expression.expressions:
            arg.accept(self)
        return self._common_return

    def visit_print_separator_statement(
        self: Linter,
        expression: PrintSeparator,
    ) -> LanguageItem:
        """Process a print separator statement."""
        del expression  # pragma: no cover
        return self._common_return  # pragma: no cover

    def visit_literal_expression(self: Linter, expression: Literal) -> LanguageItem:
        """Process a hard coded number."""
        return expression

    def visit_string_expression(self: Linter, expression: String) -> LanguageItem:
        """Process a string."""
        return expression  # pragma: no cover

    def visit_rem_statement(self: Linter, expression: RemComment) -> LanguageItem:
        """Process a comment."""
        del expression  # pragma: no cover
        return self._common_return  # pragma: no cover

    def visit_let_statement(self: Linter, expression: Let) -> LanguageItem:
        """Process an assignment."""
        expression.assign.accept(self)
        return self._common_return

    def visit_assignment_expression(
        self: Linter,
        expression: Assignment,
    ) -> LanguageItem:
        """Process an assignment."""
        # Do the right side.
        expression.expression.accept(self)

        # We have an initialization.
        self._initialized_vars.add(expression.variable.name.upper())
        return self._common_return

    def visit_variable_expression(self: Linter, variable: Variable) -> LanguageItem:
        """Process a variable."""
        # Somebody used a variable. If it's not in the initialized list, report
        # the error.
        if (name := variable.name.upper()) not in self._initialized_vars:
            msg: str = build_error_string(
                self._curr_line.source,
                f"LINT #04: Potentially uninitialized variable '{name}'.",
                variable.column,
            )
            # self._errors.append(msg)
            the_item: Linter.ErrorItem = Linter.ErrorItem(
                self._curr_line.data[0].line,
                msg,
            )
            if name not in self._potential_errors:
                self._potential_errors[name] = [the_item]
            else:
                self._potential_errors[name].append(the_item)

        return variable

    def visit_unary_expression(self: Linter, unary: Unary) -> LanguageItem:
        """Process a unary expression."""
        unary.expression.accept(self)
        return self._common_return

    def visit_binary_expression(self: Linter, binary: Binary) -> LanguageItem:
        """Process a binary expression."""
        binary.lhs.accept(self)
        binary.rhs.accept(self)
        return binary

    def visit_group_expression(self: Linter, group: Group) -> LanguageItem:
        """Process a grouped expression."""
        return group.expression.accept(self)

    def visit_random_expression(self: Linter, random: Random) -> LanguageItem:
        """Process a RND expression."""
        random.expression.accept(self)
        return self._common_return

    def visit_usr_expression(self: Linter, usr: Usr) -> LanguageItem:
        """Process a USR expression."""
        if usr.a_reg is not None:
            usr.a_reg.accept(self)
        if usr.x_reg is not None:
            usr.x_reg.accept(self)
        return self._common_return

    def _check_goto_gosub(self: Linter, cmd: str, branch: LanguageItem) -> None:
        # Evaluate the target.
        target: LanguageItem = branch.accept(self)

        # Is this a hard coded number and does it exist in the program?
        if (isinstance(target, Literal)) and (target.value not in self._lines):
            msg: str = build_error_string(
                self._curr_line.source,
                f"LINT #03: {cmd} target not in program: '{target.value}'.",
                target.column,
            )
            self._errorlist.add(Linter.ErrorItem(self._curr_line.data[0].line, msg))

    def visit_goto_statement(self: Linter, goto: Goto) -> LanguageItem:
        """Process a GOTO statement."""
        self._check_goto_gosub("GOTO", goto.target)
        return self._common_return

    def visit_gosub_statement(self: Linter, gosub: Gosub) -> LanguageItem:
        """Process a GOSUB statement."""
        self._check_goto_gosub("GOSUB", gosub.target)
        return self._common_return

    def visit_return_statement(self: Linter, ret: Return) -> LanguageItem:
        """Process a RETURN statement."""
        del ret  # pragma: no cover
        return self._common_return  # pragma: no cover

    def visit_end_statement(self: Linter, end: End) -> LanguageItem:
        """Process an END statement."""
        del end
        self._had_end_statement = True
        return self._common_return

    def visit_list_statement(self: Linter, lister: List) -> LanguageItem:
        """Process a LIST statement."""
        del lister  # pragma: no cover
        return self._common_return  # pragma: no cover

    def visit_if_statement(self: Linter, if_stmt: If) -> LanguageItem:
        """Process an IF statement."""
        if_stmt.lhs.accept(self)
        if_stmt.rhs.accept(self)
        return self._common_return

    def visit_clear_statement(self: Linter, clear: Clear) -> LanguageItem:
        """Process a CLEAR statement."""
        msg: str = build_error_string(
            self._curr_line.source,
            "LINT #02: CLEAR must never be in a program.",
            clear.column,
        )
        self._errorlist.add(Linter.ErrorItem(self._curr_line.data[0].line, msg))
        return self._common_return

    def visit_input_statement(self: Linter, input_stmt: Input) -> LanguageItem:
        """Process an INPUT statement."""
        # From the initialized variable perspective, any input will be entered
        # by the user so add them all to the good list.
        for var in input_stmt.variables:
            self._initialized_vars.add(var.name.upper())
        return self._common_return

    def visit_run_statement(self: Linter, run_stmt: Run) -> LanguageItem:
        """Process a RUN statement."""
        del run_stmt  # pragma: no cover
        return self._common_return  # pragma: no cover
