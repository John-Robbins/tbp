"""The expression and statement classes produced and used by the Parser."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2004 John Robbins
###############################################################################
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from tbp.helpers import short_int

if TYPE_CHECKING:
    from tbp.tokens import Token

# The only types allowed in value field for language items.
ValueTypes = str | int | None


class Visitor(ABC):
    """
    The visitor class for processing parsed tokens.

    This is the standard Visitor pattern discussed in the 1994 book "Design
    Patterns: Elements of Reusable Object-Oriented Software".

    Read more here: https://en.wikipedia.org/wiki/Visitor_pattern.
    """

    @abstractmethod
    def visit_linenumber_statement(
        self: Visitor,
        expression: LineNumber,
    ) -> LanguageItem:
        """Process a line number statement."""

    @abstractmethod
    def visit_print_statement(self: Visitor, expression: Print) -> LanguageItem:
        """Process a PRINT statement."""

    @abstractmethod
    def visit_print_separator_statement(
        self: Visitor,
        expression: PrintSeparator,
    ) -> LanguageItem:
        """Process a print separator statement."""

    @abstractmethod
    def visit_literal_expression(self: Visitor, expression: Literal) -> LanguageItem:
        """Process a hard coded number."""

    @abstractmethod
    def visit_string_expression(self: Visitor, expression: String) -> LanguageItem:
        """Process a string."""

    @abstractmethod
    def visit_rem_statement(self: Visitor, expression: RemComment) -> LanguageItem:
        """Process a comment."""

    @abstractmethod
    def visit_let_statement(self: Visitor, expression: Let) -> LanguageItem:
        """Process an assignment."""

    @abstractmethod
    def visit_assignment_expression(
        self: Visitor,
        expression: Assignment,
    ) -> LanguageItem:
        """Process an assignment."""

    @abstractmethod
    def visit_variable_expression(self: Visitor, variable: Variable) -> LanguageItem:
        """Process a variable."""

    @abstractmethod
    def visit_unary_expression(self: Visitor, unary: Unary) -> LanguageItem:
        """Process a unary expression."""

    @abstractmethod
    def visit_binary_expression(self: Visitor, binary: Binary) -> LanguageItem:
        """Process a binary expression."""

    @abstractmethod
    def visit_group_expression(self: Visitor, group: Group) -> LanguageItem:
        """Process a grouped expression."""

    @abstractmethod
    def visit_random_expression(self: Visitor, random: Random) -> LanguageItem:
        """Process a RND expression."""

    @abstractmethod
    def visit_usr_expression(self: Visitor, usr: Usr) -> LanguageItem:
        """Process a USR expression."""

    @abstractmethod
    def visit_goto_statement(self: Visitor, goto: Goto) -> LanguageItem:
        """Process a GOTO statement."""

    @abstractmethod
    def visit_gosub_statement(self: Visitor, gosub: Gosub) -> LanguageItem:
        """Process a GOSUB statement."""

    @abstractmethod
    def visit_return_statement(self: Visitor, ret: Return) -> LanguageItem:
        """Process a RETURN statement."""

    @abstractmethod
    def visit_end_statement(self: Visitor, end: End) -> LanguageItem:
        """Process an END statement."""

    @abstractmethod
    def visit_list_statement(self: Visitor, lister: List) -> LanguageItem:
        """Process a LIST statement."""

    @abstractmethod
    def visit_if_statement(self: Visitor, if_stmt: If) -> LanguageItem:
        """Process an IF statement."""

    @abstractmethod
    def visit_clear_statement(self: Visitor, clear: Clear) -> LanguageItem:
        """Process a CLEAR statement."""

    @abstractmethod
    def visit_input_statement(self: Visitor, input_stmt: Input) -> LanguageItem:
        """Process an INPUT statement."""

    @abstractmethod
    def visit_run_statement(self: Visitor, run_stmt: Run) -> LanguageItem:
        """Process a RUN statement."""


###############################################################################
# A Program Line
###############################################################################


@dataclass
class ProgramLine:
    """
    The class that represents a parsed program line.

    Used by the Interpreter and Linter classes
    """

    # The source code text.
    source: str
    # The parsed data for the line.
    data: list[LanguageItem]


###############################################################################
# Base Classes
###############################################################################


class LanguageItem:
    """
    The base class for all language items used by tbp.

    This class has a value field in it that can be used to store the value of
    the item or any other information that might be needed.
    """

    def __init__(
        self: LanguageItem,
        line: int,
        column: int,
        value: ValueTypes = None,
    ) -> None:
        """Initialize the class."""
        self._value: ValueTypes = value
        if isinstance(self._value, int) is True:
            # Only accept the last two bytes. Memory was expensive in 1976.
            self._value = short_int(cast(int, self._value))
        self.line = line
        self.column = column

    @property
    def value(self: LanguageItem) -> ValueTypes:
        """Get the value for this language item."""
        return self._value

    @value.setter
    def value(self: LanguageItem, new_value: ValueTypes) -> None:
        """Set the value for this language item."""
        if isinstance(new_value, int) is True:
            self._value = short_int(cast(int, new_value))
        else:
            self._value = new_value

    def __repr__(self: LanguageItem) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: v={self.value}"

    @abstractmethod
    def accept(self: LanguageItem, visitor: Visitor) -> LanguageItem:
        """Process this language item."""


###############################################################################
# Expression Types
###############################################################################


class Literal(LanguageItem):
    """A hard coded numbers."""

    def __init__(self: Literal, line: int, column: int, value: int) -> None:
        """Initialize the class."""
        super().__init__(line, column, value)

    def __repr__(self: Literal) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: v={self.value}"

    def accept(self: Literal, visitor: Visitor) -> LanguageItem:
        """Produce the hardcoded number."""
        return visitor.visit_literal_expression(self)


class String(LanguageItem):
    """A string for the PRINT statement."""

    def __init__(self: String, line: int, column: int, value: str) -> None:
        """Initialize the class."""
        super().__init__(line, column, value)

    def __repr__(self: String) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: v={self.value}"

    def accept(self: String, visitor: Visitor) -> LanguageItem:
        """Produce the string."""
        return visitor.visit_string_expression(self)


class Variable(LanguageItem):
    """A variable."""

    def __init__(self: Variable, line: int, column: int, name: str) -> None:
        """Initialize the class."""
        self.name = name
        super().__init__(line, column)

    def __repr__(self: Variable) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: name={self.name}"

    def accept(self: Variable, visitor: Visitor) -> LanguageItem:
        """Produce the variable."""
        return visitor.visit_variable_expression(self)


class Assignment(LanguageItem):
    """When variable = value."""

    def __init__(
        self: Assignment,
        line: int,
        column: int,
        variable: Variable,
        expression: LanguageItem,
    ) -> None:
        """Initialize the class."""
        self.variable = variable
        self.expression = expression
        super().__init__(line, column)

    def __repr__(self: Assignment) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: Var={self.variable} Ex={self.expression}"

    def accept(self: Assignment, visitor: Visitor) -> LanguageItem:
        """Produce the assignment."""
        return visitor.visit_assignment_expression(self)


class Unary(LanguageItem):
    """When a + or - prefixes an expression."""

    def __init__(
        self: Unary,
        line: int,
        column: int,
        operator: Token,
        expression: LanguageItem,
    ) -> None:
        """Initialize the class."""
        self.operator: Token = operator
        self.expression: LanguageItem = expression
        super().__init__(line, column)

    def __repr__(self: Unary) -> str:
        """Get the display information."""
        return (
            f"{type(self).__qualname__}: Op={self.operator.lexeme} Ex={self.expression}"
        )

    def accept(self: Unary, visitor: Visitor) -> LanguageItem:
        """Produce a unary expression."""
        return visitor.visit_unary_expression(self)


class Binary(LanguageItem):
    """Handle expressions like 'A+B'."""

    def __init__(
        self: Binary,
        line: int,
        column: int,
        lhs: LanguageItem,
        operator: Token,
        rhs: LanguageItem,
    ) -> None:
        """Initialize the class."""
        self.lhs: LanguageItem = lhs
        self.operator: Token = operator
        self.rhs: LanguageItem = rhs
        super().__init__(line, column)

    def __repr__(self: Binary) -> str:
        """Get the display information."""
        return (
            f"{type(self).__qualname__}: Lhs={self.lhs} "
            f"Op={self.operator.lexeme} Rhs={self.rhs}"
        )

    def accept(self: Binary, visitor: Visitor) -> LanguageItem:
        """Produce a binary expression."""
        return visitor.visit_binary_expression(self)


class Group(LanguageItem):
    """Handle an expression inside parenthesis."""

    def __init__(self: Group, line: int, column: int, expression: LanguageItem) -> None:
        """Initialize the class."""
        self.expression = expression
        super().__init__(line, column)

    def __repr__(self: Group) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: Ex={self.expression}"

    def accept(self: Group, visitor: Visitor) -> LanguageItem:
        """Produce a group expression."""
        return visitor.visit_group_expression(self)


class Random(LanguageItem):
    """The RND expression processing."""

    def __init__(
        self: Random,
        line: int,
        column: int,
        expression: LanguageItem,
    ) -> None:
        """Initialize the class."""
        self.expression = expression
        super().__init__(line, column)

    def __repr__(self: Random) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: Ex={self.expression}"

    def accept(self: Random, visitor: Visitor) -> LanguageItem:
        """Produce a RND expression."""
        return visitor.visit_random_expression(self)


class Usr(LanguageItem):
    """The USR expression processing."""

    def __init__(
        self: Usr,
        line: int,
        column: int,
        subroutine: LanguageItem,
        x_reg: LanguageItem | None,
        a_reg: LanguageItem | None,
    ) -> None:
        """Initialize the class."""
        # The routine to access.
        self.subroutine = subroutine
        # The index register value.
        self.x_reg = x_reg
        # The accumulator register value.
        self.a_reg = a_reg
        super().__init__(line, column)

    def __repr__(self: Usr) -> str:
        """Get the display information."""
        return (
            f"{type(self).__qualname__}: Subroutine={self.subroutine}"
            f"x={self.x_reg} a={self.a_reg}"
        )

    def accept(self: Usr, visitor: Visitor) -> LanguageItem:
        """Produce a USR expression."""
        return visitor.visit_usr_expression(self)


###############################################################################
# Statement Types
###############################################################################


class LineNumber(LanguageItem):
    """A line number statement."""

    def __init__(self: LineNumber, line: int, column: int, value: ValueTypes) -> None:
        """Initialize the class."""
        super().__init__(line, column, value)

    def __repr__(self: LineNumber) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: v={self.value}"

    def accept(self: LineNumber, visitor: Visitor) -> LanguageItem:
        """Process a line number."""
        return visitor.visit_linenumber_statement(self)


class PrintSeparator(LanguageItem):
    """A comma or semicolon separator in the PRINT statement."""

    def __init__(
        self: PrintSeparator,
        line: int,
        column: int,
        separator: ValueTypes,
    ) -> None:
        """Initialize the class."""
        self.separator = separator
        super().__init__(line, column)

    def __repr__(self: PrintSeparator) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: s={self.separator}"

    def accept(self: PrintSeparator, visitor: Visitor) -> LanguageItem:
        """There is nothing to do with a print separator."""
        return visitor.visit_print_separator_statement(self)


class Print(LanguageItem):
    """A PRINT statement."""

    def __init__(
        self: Print,
        line: int,
        column: int,
        expressions: list[LanguageItem],
    ) -> None:
        """Initialize the class."""
        self.expressions = expressions
        super().__init__(line, column)

    def __repr__(self: Print) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: exp={self.expressions}"

    def accept(self: Print, visitor: Visitor) -> LanguageItem:
        """Do the PRINT statement."""
        return visitor.visit_print_statement(self)


class RemComment(LanguageItem):
    """A REM statement."""

    def __init__(self: RemComment, line: int, column: int, value: str) -> None:
        """Initialize the class."""
        super().__init__(line, column, value)

    def __repr__(self: RemComment) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: exp={self.value}"

    def accept(self: RemComment, visitor: Visitor) -> LanguageItem:
        """Do the REM statement."""
        return visitor.visit_rem_statement(self)


class Let(LanguageItem):
    """A LET statement."""

    def __init__(self: Let, line: int, column: int, assign: Assignment) -> None:
        """Initialize the class."""
        self.assign: Assignment = assign
        super().__init__(line, column)

    def __repr__(self: Let) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: exp={self.assign}"

    def accept(self: Let, visitor: Visitor) -> LanguageItem:
        """Do the LET statement."""
        return visitor.visit_let_statement(self)


class Branch(LanguageItem):
    """A base class for GOTO and GOSUB to make branch analysis easier."""

    def __init__(self: Branch, line: int, column: int, target: LanguageItem) -> None:
        """Initialize the class."""
        self.target: LanguageItem = target
        super().__init__(line, column)

    @abstractmethod
    def accept(self: LanguageItem, visitor: Visitor) -> LanguageItem:
        """Process this language item."""


class Goto(Branch):
    """A GOTO statement."""

    def __init__(self: Goto, line: int, column: int, target: LanguageItem) -> None:
        """Initialize the class."""
        super().__init__(line, column, target)

    def __repr__(self: Goto) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: exp={self.target}"

    def accept(self: Goto, visitor: Visitor) -> LanguageItem:
        """Do the GOTO statement."""
        return visitor.visit_goto_statement(self)


class Gosub(Branch):
    """A GOSUB statement."""

    def __init__(self: Gosub, line: int, column: int, target: LanguageItem) -> None:
        """Initialize the class."""
        self.target: LanguageItem = target
        super().__init__(line, column, target)

    def __repr__(self: Gosub) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}: exp={self.target}"

    def accept(self: Gosub, visitor: Visitor) -> LanguageItem:
        """Do the GOSUB statement."""
        return visitor.visit_gosub_statement(self)


class Return(LanguageItem):
    """A RETURN statement."""

    def __init__(
        self: Return,
        line: int,
        column: int,
    ) -> None:
        """Initialize the class."""
        super().__init__(line, column)

    def __repr__(self: Return) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}"

    def accept(self: Return, visitor: Visitor) -> LanguageItem:
        """Do the RETURN statement."""
        return visitor.visit_return_statement(self)


class End(LanguageItem):
    """An END statement."""

    def __init__(
        self: End,
        line: int,
        column: int,
    ) -> None:
        """Initialize the class."""
        super().__init__(line, column)

    def __repr__(self: End) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}"

    def accept(self: End, visitor: Visitor) -> LanguageItem:
        """Do the END statement."""
        return visitor.visit_end_statement(self)


class List(LanguageItem):
    """A LIST statement."""

    def __init__(
        self: List,
        line: int,
        column: int,
        start_line: LanguageItem,
        end_line: LanguageItem,
    ) -> None:
        """Initialize the class."""
        self.start_line = start_line
        self.end_line = end_line
        super().__init__(line, column)

    def __repr__(self: List) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__} s={self.start_line} e={self.end_line}"

    def accept(self: List, visitor: Visitor) -> LanguageItem:
        """Do the LIST statement."""
        return visitor.visit_list_statement(self)


class If(LanguageItem):
    """An IF statement."""

    def __init__(
        self: If,
        line: int,
        column: int,
        lhs: LanguageItem,
        operator: Token,
        rhs: LanguageItem,
        branch: LanguageItem,
    ) -> None:
        """Initialize the class."""
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs
        self.branch = branch
        super().__init__(line, column)

    def __repr__(self: If) -> str:
        """Get the display information."""
        return (
            f"{type(self).__qualname__} l={self.lhs} o={self.operator.lexeme}"
            f" r={self.rhs} b={self.branch}"
        )

    def accept(self: If, visitor: Visitor) -> LanguageItem:
        """Do the IF statement."""
        return visitor.visit_if_statement(self)


class Clear(LanguageItem):
    """A CLEAR statement."""

    def __init__(
        self: Clear,
        line: int,
        column: int,
    ) -> None:
        """Initialize the class."""
        super().__init__(line, column)

    def __repr__(self: Clear) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__}"

    def accept(self: Clear, visitor: Visitor) -> LanguageItem:
        """Do the CLEAR statement."""
        return visitor.visit_clear_statement(self)


class Input(LanguageItem):
    """A INPUT statement."""

    def __init__(
        self: Input,
        line: int,
        column: int,
        variables: list[Variable],
    ) -> None:
        """Initialize the class."""
        self.variables = variables
        super().__init__(line, column)

    def __repr__(self: Input) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__} v={self.variables}"

    def accept(self: Input, visitor: Visitor) -> LanguageItem:
        """Do the INPUT statement."""
        return visitor.visit_input_statement(self)


class Run(LanguageItem):
    """A RUN statement."""

    def __init__(
        self: Run,
        line: int,
        column: int,
        input_values: list[LanguageItem],
    ) -> None:
        """Initialize the class."""
        self.input_values = input_values
        super().__init__(line, column)

    def __repr__(self: Run) -> str:
        """Get the display information."""
        return f"{type(self).__qualname__} v={self.input_values}"

    def accept(self: Run, visitor: Visitor) -> LanguageItem:
        """RUN, FOREST. RUN."""
        return visitor.visit_run_statement(self)
