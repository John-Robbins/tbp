"""The tree walking interpreter and debugger for Tiny BASIC in Python."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2004 John Robbins
###############################################################################
from __future__ import annotations

import time
from enum import Enum, auto
from io import StringIO
from secrets import randbelow
from typing import TYPE_CHECKING, cast

from sortedcontainers import SortedDict, SortedList

from tbp.astprinter import AstPrinter
from tbp.errors import TbpBaseError, TbpRuntimeError
from tbp.helpers import build_error_string, print_output, read_input, tbp_logger
from tbp.languageitems import (
    Assignment,
    Branch,
    Clear,
    End,
    Gosub,
    Goto,
    If,
    Input,
    LanguageItem,
    Let,
    LineNumber,
    List,
    Print,
    PrintSeparator,
    ProgramLine,
    Return,
    Run,
    Visitor,
)
from tbp.linter import Linter
from tbp.memory import Memory
from tbp.parser import Parser
from tbp.scanner import Scanner
from tbp.symboltable import SymbolTable
from tbp.tokens import TokenType

if TYPE_CHECKING:
    from tbp.languageitems import (
        Binary,
        Group,
        Literal,
        Random,
        RemComment,
        String,
        Unary,
        Usr,
        Variable,
    )
    from tbp.symboltable import SymbolInfo
    from tbp.tokens import Token


class Interpreter(Visitor):
    """
    The tree walking interpreter and debugger.

    This class is designed to be held by a host and continually used for both
    direct execution and programmatic Tiny BASIC code. The interpret method can
    work with single lines and entire buffers with lines separated by CRLF.
    """

    class State(Enum):
        """The processing states for the interpreter."""

        # The default state where we are processing lines as the user types
        # them in.
        LINE_STATE = auto()
        # We are reading and processing lines out of a file.
        FILE_STATE = auto()
        # We are executing the program.
        RUNNING_STATE = auto()
        # We hit a breakpoint.
        BREAK_STATE = auto()
        # We are reading lines out of a file, but had an earlier error so
        # continue parsing and reporting additional errors, but don't execute
        # any code.
        ERROR_FILE_STATE = auto()

    class BreakContinueType(Enum):
        """How to continue from a breakpoint."""

        # Continue running.
        RUN = auto()
        # Single step.
        STEP = auto()

    ###########################################################################
    # PUBLIC: Initialization
    ###########################################################################

    def __init__(self: Interpreter) -> None:
        """Initialize the instance."""
        self._logger = tbp_logger()
        self._scanner: Scanner = Scanner()
        self._parser: Parser = Parser()
        self._symbol_table: SymbolTable = SymbolTable()
        # By convention, TINY BASIC uses the S variable as the base address for
        # the read and write memory routines. For convenience, I'll emulate the
        # standard Motorola 6800 CPU. Note that this is the only place where
        # this is set so if the user changes it later, it's on them.
        self._symbol_table["S"] = 256
        # The AstPrinter is only used when logging is turned on.
        self._ast_printer: AstPrinter = AstPrinter()
        self._lines: SortedDict[int, ProgramLine] = SortedDict()
        # If true, time the line execution. Note that this is a public
        # property. It's not part of the reinitialization in case the user had
        # set it earlier.
        self.time_lines = False
        # The list of breakpoints.
        self._breakpoints: SortedList[int] = SortedList()
        # A flag to indicate if breakpoints are enabled. See the discussion in
        # _run_program as to why we do this.
        self._breakpoints_enabled: bool = True
        #######################################################################
        # BIG NOTE! If you add any values to __init__, after this comment, make
        # sure to also initialize then in the _initialize_runtime_state method.
        # The current ***FILE*** line number.
        self._file_line: int = 1
        # The current state in the interpreter.
        self._the_state: Interpreter.State = Interpreter.State.LINE_STATE
        # The instruction pointer for executing lines.
        self._ip: int = 0
        # If not equal to zero, holds the GOTO, GOSUB, or RETURN address.
        self._branch_ip = 0
        # The call stack for GOSUB and RETURN.
        self._callstack: list[int] = []
        # Parameters passed to the direct execution RUN command that are to
        # be used for INPUT values.
        self._run_params: list[LanguageItem] = []
        # The fake memory for the USR function.
        self._mem: Memory = Memory()
        # The one-shot breakpoints list.
        self._one_shot_breakpoints: list[int] = []

    ###########################################################################
    # PUBLIC: Interpret Methods
    ###########################################################################

    def interpret_line(self: Interpreter, source: str) -> bool:
        """
        Interpret and execute a line of Tiny BASIC code.

        Parameter
        ---------
        source - The textual representation of Tiny BASIC code line to execute.

        Returns
        -------
        True  - The code line was parsed and executed without errors.
        False - There was an error parsing or executing.

        """
        # Set to False if there was an error parsing.
        good_parse: bool = True
        try:
            # Scan and parse.
            lex_tokens: list[Token] = self._scanner.scan_tokens(source)
            tokens: list[LanguageItem] = self._parser.parse_tokens(lex_tokens)

            # Dump the tokens for debugging.
            self._logger.debug("Parsing:\n%s", self._ast_printer.print(tokens))
            self._logger.debug("Interpreter state: %s", str(self._the_state))

            # Execute the code if we are not in an error state.
            if self._the_state != Interpreter.State.ERROR_FILE_STATE:
                # Here's something. I've specifically declared line_num as
                # an integer and tokens[0].value is of type "str|int|None."
                # Why can't mypy pick up the type from the declaration of the
                # variable type?
                line_num: int = cast(int, tokens[0].value)
                # Take a look at the first element. If it is a LineNumber we
                # store it in the program.
                if isinstance(tokens[0], LineNumber) is True:
                    # Does the user want to delete a line?
                    if len(tokens) == 1:
                        self._delete_program_line(line_num)
                    else:
                        # Remove any trailing '\n' or whitespace.
                        temp: str = source.rstrip()
                        self._lines[line_num] = ProgramLine(temp, tokens)
                else:
                    # This is a direct execution request.
                    for token in tokens:
                        self._evaluate(token)

        # Both syntax and runtime errors are handled here.
        except TbpBaseError as err:
            # Are we at a breakpoint and did the user type something invalid
            # such as "opt log f" where they forgot the bug splat (%)?
            if self._the_state != Interpreter.State.BREAK_STATE:
                # Given that something bad happened, let's reset the state to get
                # back to a known state.
                self.initialize_runtime_state()
            good_parse = False
            self._report_error(source, err)

        return good_parse

    def interpret_buffer(self: Interpreter, source: str) -> bool:
        """
        Interpret and execute an a buffer of Tiny BASIC lines to execute..

        Parameter
        ---------
        source - A buffer with Tiny BASIC lines separated by CRLF.

        Returns
        -------
        True  - The code chunk was parsed and executed without errors.
        False - There was an error parsing or executing.

        """
        final_return: bool = True
        try:
            # Set the state flag so other methods know we are parsing a buffer.
            self._the_state = Interpreter.State.FILE_STATE
            # Set to False if there was an error parsing.
            self._file_line = 1

            # Fake reading this memory buffer as a file. I like this trick.
            file = StringIO(source)

            current_line: str = file.readline()
            while current_line:
                # It's perfectly fine to have empty lines.
                if (current_line != "\n") and (
                    self.interpret_line(current_line) is False
                ):
                    self._the_state = Interpreter.State.ERROR_FILE_STATE
                    final_return = False
                current_line = file.readline()
                self._file_line += 1

            if self._the_state == Interpreter.State.ERROR_FILE_STATE:
                # Clear out any loaded program so we don't have half programs
                # floating around.
                self.clear_program()
                self.initialize_runtime_state()
        finally:
            self._the_state = Interpreter.State.LINE_STATE

        return final_return

    ###########################################################################
    # PUBLIC: Program and line retrieval.
    ###########################################################################
    def get_program(self: Interpreter) -> str:
        """Get the entire text of the program loaded in memory."""
        if len(self._lines) == 0:
            return ""

        program: str = ""
        for line in self._lines:
            program += f"{self._lines[line].source}\n"

        return program

    def current_line_number(self: Interpreter) -> int:
        """Get the current instruction pointer, i.e., the line number."""
        return self._ip

    ###########################################################################
    # PUBLIC: State management methods.
    ###########################################################################

    def initialize_runtime_state(self: Interpreter) -> None:
        """Initialize all the runtime state variables to a known state."""
        self._the_state = Interpreter.State.LINE_STATE
        self._ip = 0
        self._branch_ip = 0
        self._callstack = []
        self._run_params = []
        self._mem = Memory()
        self._one_shot_breakpoints = []

    def clear_program(self: Interpreter) -> None:
        """Remove any program in memory."""
        self._lines.clear()
        self._breakpoints.clear()
        self._one_shot_breakpoints = []

    ###########################################################################
    # PUBLIC: Debugger related methods.
    ###########################################################################

    def variables_string(self: Interpreter) -> str:
        """Return the string for display of initialized variables."""
        return self._symbol_table.values_string()

    def set_breakpoint(self: Interpreter, line_number: int) -> tuple[bool, str]:
        """Set a breakpoint on the specified line."""
        # First check if this line is in the program.
        if line_number not in self._lines:
            return (
                False,
                f"CLE #06: Line does not exist in the program: '{line_number}'.",
            )

        if line_number in self._breakpoints:
            return False, f"CLE #14: Breakpoint already set on '{line_number}'."

        # Set the breakpoint into the breakpoint list.
        self._breakpoints.add(line_number)

        return True, ""

    def list_breakpoints(self: Interpreter) -> str:
        """Return the string showing what breakpoints are set."""
        if len(self._breakpoints) == 0:
            return "No breakpoints set.\n"

        ret_str: str = "Breakpoints set on:\n"
        for num in self._breakpoints:
            ret_str += f"{self._lines[num].source}\n"

        return ret_str

    def delete_all_breakpoints(self: Interpreter) -> None:
        """Delete all breakpoints."""
        self._breakpoints.clear()

    def delete_breakpoint(self: Interpreter, line_number: int) -> tuple[bool, str]:
        """Delete a breakpoint."""
        if line_number not in self._breakpoints:
            return (
                False,
                f"CLE #06: Line does not exist in the program: '{line_number}'.",
            )

        self._breakpoints.remove(line_number)
        return True, ""

    def at_breakpoint(self: Interpreter) -> bool:
        """Public method the driver can call to see the state."""
        return self._the_state == Interpreter.State.BREAK_STATE

    def break_continue(self: Interpreter, step: Interpreter.BreakContinueType) -> None:
        """Tell the interpreter how to continue from a breakpoint."""
        # We have to be very careful here. The debugger evaluation is called
        # out of band compared to normal execution. If the address for the
        # branch is invalid, tbp throws an exception and will crash the whole
        # program. I'll trap and report here as crashing the whole program when
        # debugging does not make for a great user experience.
        try:
            if step == Interpreter.BreakContinueType.STEP:
                self._set_one_shots()

            # The line we are at in _ip needs to be run so let fly.
            self._run_program(self._ip)
        except TbpBaseError as err:
            # I won't reset state like we do in the normal error processing so
            # the user can inspect the program.
            self._report_error("Debugger evaluation", err)

    def stack_string(self: Interpreter) -> str:
        """Return the string of the current call stack."""
        result: str = "-- Call Stack --\n"

        for frame in reversed(self._callstack):
            result += f"{self._lines[frame].source}\n"

        return result

    ###########################################################################
    # PUBLIC: Linting methods
    ###########################################################################

    # https://docs.astral.sh/ruff/rules/boolean-type-hint-positional-argument/
    # I know, but sometimes you just need a simple flag.
    def lint_program(self: Interpreter, strict: bool) -> None:  # noqa: FBT001
        """Lints the program in memory."""
        # If there's no program loaded, just return.
        if len(self._lines) == 0:
            return

        linter: Linter = Linter()

        linter.lint_program(self._lines, strict)

    ###########################################################################
    # PRIVATE: Helper methods
    ###########################################################################

    def _evaluate(self: Interpreter, expression: LanguageItem) -> LanguageItem:
        """Evaluate an expression/statement."""
        # Yes, it's just a wrapper but I think it makes it clearer what we are
        # doing in the interpreter.
        return expression.accept(self)

    def _delete_program_line(self: Interpreter, line_num: int) -> None:
        """Delete a program line and if a BP is set, delete it as well."""
        # We don't allow deleting lines if stopped at a breakpoint. The havoc
        # would be immense! 😱 Changing a list as you enumerate it is not a
        # healthy lifestyle choice.
        if self._the_state == Interpreter.State.BREAK_STATE:
            print_output(
                "CLE #09: Deleting program lines while debugging disabled.\n",
            )
            return

        if line_num in self._lines:
            self._lines.pop(line_num, None)
        # Only report missing lines in interactive mode.
        elif self._the_state != Interpreter.State.FILE_STATE:
            print_output(
                f"Error #347: Line number is not in the program: '{line_num}'\n",
            )
        # If the line has a BP on it. delete it as well.
        if line_num in self._breakpoints:
            self._breakpoints.remove(line_num)

    def _report_error(
        self: Interpreter,
        source: str,
        err: TbpBaseError,
    ) -> None:
        """Report a syntax or a runtime error."""
        # If the line number is from the program, get the source line to report
        # the error on the correct line. Otherwise, the source parameter is the
        # direct execution statement.
        if (err.line != 0) and (err.line in self._lines):
            source = self._lines[err.line].source
        msg = f"{err.friendly_name}: {err.message}"
        if self._the_state != Interpreter.State.LINE_STATE:
            msg += f" (file line {self._file_line})"
        full: str = build_error_string(source, msg, err.column)
        print_output(full)

    @staticmethod
    def _raise_error(line: int, column: int, message: str) -> None:
        """Report a runtime error by raising a TbpRuntimeError."""
        error: TbpRuntimeError = TbpRuntimeError(line, column, message)
        raise error

    def _run_line(self: Interpreter, line: int) -> None:
        """Execute the specific line."""
        self._logger.debug("Executing: `%s`", self._lines[line].source)
        start = time.time()
        self._evaluate(self._lines[line].data[1])
        end = time.time()
        if self.time_lines is True:
            final = round((end - start) * 1000, 5)
            print_output(f"[{line}] = {final} ms\n")

    def _get_next_line(self: Interpreter, line: int) -> int:
        """Return the next line in the program."""
        # Get the index into the keys for this line number.
        if (index := self._lines.keys().index(line)) == len(self._lines) - 1:
            return 0
        return self._lines.keys()[index + 1]

    def _run_program(self: Interpreter, start_line: int = 0) -> None:
        """Execute a loaded program."""
        # If start_line is something other than 0, that means we are asked to
        # continue or step after a breakpoint. As the breakpoint stops before
        # the line is executed, if we didn't disable the breakpoints, we'd be
        # stuck in a break/execute infinite loop. Once we execute the line that
        # had the breakpoint, we reenable them so we can break again when it's
        # executed.
        self._breakpoints_enabled = True

        # Get the first line of the program into the instruction pointer.
        if start_line == 0:
            self._ip = self._lines.keys()[0]
        else:
            # Restarting from a breakpoint.
            self._ip = start_line
            self._breakpoints_enabled = False

        # Setup any other state and tell the world we are running.
        self._branch_ip = 0
        self._the_state = Interpreter.State.RUNNING_STATE

        while self._the_state == Interpreter.State.RUNNING_STATE:
            # Have we hit a breakpoint?
            if self._hit_breakpoint() is False:
                # Reset the breakpoints to be enabled.
                self._breakpoints_enabled = True
                # No breakpoints so run like normal.
                self._run_line(self._ip)
                # A little sanity check to ensure we are still running as we
                # don't want to do this work if we are done. Any call to
                # _run_line can change the state.
                if self._the_state == Interpreter.State.RUNNING_STATE:
                    # Are we supposed to branch?
                    if self._branch_ip != 0:
                        self._ip = self._branch_ip
                        self._branch_ip = 0
                    else:
                        # No branching, so get the next line in the program.
                        self._ip = self._get_next_line(self._ip)
                # An instruction pointer of zero means we are done, or had an
                # error during the run so end execution.
                if self._ip == 0:
                    break

        if self._the_state == Interpreter.State.RUNNING_STATE:
            # Set the execution state back to a known state.
            self.initialize_runtime_state()
            print_output("Error #335: No END in the program.\n")

    def _hit_breakpoint(self: Interpreter) -> bool:
        """Report if hit a breakpoint."""
        if self._breakpoints_enabled is False:
            return False

        if self._ip in self._breakpoints:
            print_output(f"Breakpoint: {self._ip}\n")
            self._the_state = Interpreter.State.BREAK_STATE
        elif self._ip in self._one_shot_breakpoints:
            # Clear the one shot.
            self._one_shot_breakpoints = []
            self._the_state = Interpreter.State.BREAK_STATE

        # In either case, display the line.
        if self._the_state == Interpreter.State.BREAK_STATE:
            print_output(f"[{self._lines[self._ip].source}]\n")
            return True

        return False

    def _set_one_shots(self: Interpreter) -> None:  # noqa: C901 pylint: disable=too-complex
        """
        Find the address to step into.

        Given the following code:

        100 IF H=1 GOSUB 200
        110 PR "Blah!"

        The instruction pointer is on line 100 when the user does %s.

        This method will set two one shot breakpoints (two shots?). The first
        is on 200 because of the GOSUB. The second is on 110 as that is the
        next line.

        Some special case scenarios:

        100 IF P=1 IF J=2 GOTO 333
            - This code has to handle nested IF statements.

        200 END
        <EOF>
            - With line 200 being the last line in the file, and not having any
              branching instruction, there is no next line so no one shots
              will be set.

        135 RETURN
            - A one shot will only be set on the return address from the call
              stack.
        """

        # Helper to check GOTO/GOSUB. I do have to admit I like the "declare
        # functions inside functions/methods" capabilities in Python.
        def do_branch(branch: Branch) -> None:
            br_address: LanguageItem = self._evaluate(branch.target)
            if (line := cast(int, br_address.value)) not in self._lines:
                print_output(f"CLE #10: Branch target does not exist '{line}'.\n")
                return
            self._one_shot_breakpoints.append(cast(int, br_address.value))

        def do_if(if_stmt: If) -> None:
            # We care about two things in the IF branch field, is it another IF
            # or a GOTO/GOSUB.
            if isinstance(if_stmt.branch, Branch):
                do_branch(if_stmt.branch)
            elif isinstance(if_stmt.branch, If):
                # Captain Recursion!
                do_if(if_stmt.branch)

        # We have to look for IF, RETURN, GOTO, and GOSUB as they are the
        # special.
        stmt = self._lines[self._ip].data[1]
        if isinstance(stmt, Return):
            # A RETURN statement is different in that I need to grab the
            # first item on the stack as that's where we are going to end
            # up.
            if len(self._callstack) == 0:
                print_output("CLE #11: RETURN call stack is empty.")
                return
            self._one_shot_breakpoints.append(self._callstack[len(self._callstack) - 1])
            return
        if isinstance(stmt, Branch):
            do_branch(stmt)
        if isinstance(stmt, If):
            do_if(stmt)

        # Last thing to get is the next line, but only add if not 0.
        if (next_line := self._get_next_line(self._ip)) != 0:
            self._one_shot_breakpoints.append(next_line)

        self._logger.debug("One shot breakpoints: %s", str(self._one_shot_breakpoints))

    ###########################################################################
    # PRIVATE: Visit methods
    ###########################################################################

    def visit_linenumber_statement(
        self: Interpreter,
        expression: LineNumber,
    ) -> LanguageItem:
        """Process a line number statement."""
        del expression  # pragma: no cover
        return cast(LineNumber, None)  # pragma: no cover

    def visit_print_statement(
        self: Interpreter,
        expression: Print,
    ) -> LanguageItem:
        """Process a PRINT statement."""
        # Our job here is to loop through expression.expression and build a
        # string to output.
        expression_count: int = len(expression.expressions)

        # Is this a call to PRINT with no parameters?
        if len(expression.expressions) == 0:
            print_output("\n")
        else:
            # The output string we will build up.
            builder: str = ""
            for item in expression.expressions:
                if isinstance(item, PrintSeparator) is True:
                    temp: PrintSeparator = cast(PrintSeparator, item)
                    if temp.separator == ",":
                        to_add = " " * (8 - (len(builder) % 8))
                        builder += to_add
                else:
                    result: LanguageItem = self._evaluate(item)
                    builder += str(result.value)

            # If the last item in the print expressions is ',' or ';' do not
            # add the CRLF to the output.
            last_item: LanguageItem = expression.expressions[expression_count - 1]
            if isinstance(last_item, PrintSeparator) is False:
                builder += "\n"
            print_output(builder)

        # I want to return None so if something tries to use this result, we
        # crash.
        return cast(Print, None)

    def visit_print_separator_statement(
        self: Interpreter,
        expression: PrintSeparator,
    ) -> LanguageItem:
        """Process a print separator statement."""
        del expression  # pragma: no cover
        return cast(Let, None)  # pragma: no cover

    def visit_literal_expression(
        self: Interpreter,
        expression: Literal,
    ) -> LanguageItem:
        """Process a hard coded number."""
        return expression

    def visit_string_expression(self: Interpreter, expression: String) -> LanguageItem:
        """Process a string."""
        return expression

    def visit_rem_statement(self: Interpreter, expression: RemComment) -> LanguageItem:
        """Process a comment."""
        return expression

    def visit_let_statement(self: Interpreter, expression: Let) -> LanguageItem:
        """Process an assignment."""
        # Do the assignment.
        self._evaluate(expression.assign)
        return cast(Let, None)

    def visit_assignment_expression(
        self: Interpreter,
        expression: Assignment,
    ) -> LanguageItem:
        """Process an assignment."""
        # Evaluate the right hand side.
        exp: LanguageItem = self._evaluate(expression.expression)
        var: str = expression.variable.name.upper()
        self._symbol_table[var] = cast(int, exp.value)
        return cast(Assignment, None)

    def visit_variable_expression(
        self: Interpreter,
        variable: Variable,
    ) -> LanguageItem:
        """Process a variable."""
        # Look the variable up in the symbol table.
        var: str = variable.name.upper()
        symbol: SymbolInfo = self._symbol_table[var]
        if symbol.initialized is False:
            self._raise_error(
                variable.line,
                variable.column,
                f"Error #336: Accessing uninitialized variable '{var}'.",
            )
        variable.value = symbol.value
        return variable

    def visit_unary_expression(self: Interpreter, unary: Unary) -> LanguageItem:
        """Process a unary expression."""
        right: LanguageItem = self._evaluate(unary.expression)
        value: int = cast(int, right.value)
        value = -value if unary.operator.tbp_type == TokenType.MINUS else abs(value)
        unary.value = value
        return unary

    def visit_binary_expression(self: Interpreter, binary: Binary) -> LanguageItem:
        """Process a binary expression."""
        # Before anything else, evaluate both sides of the binary expression.
        left: LanguageItem = self._evaluate(binary.lhs)
        right: LanguageItem = self._evaluate(binary.rhs)

        # Grab the left and right values.
        left_value = left.value
        right_value = right.value

        # Holds the result.
        result: int = 0

        match binary.operator.tbp_type:
            case TokenType.PLUS:
                result = cast(int, left_value) + cast(int, right_value)
            case TokenType.MINUS:
                result = cast(int, left_value) - cast(int, right_value)
            case TokenType.STAR:
                result = cast(int, left_value) * cast(int, right_value)
            case TokenType.SLASH:
                if right_value == 0:
                    self._raise_error(
                        binary.line,
                        binary.column,
                        "Error #224 Division by zero.",
                    )
                # The '//' operator is the floor division operator. It returns
                # the quotient part of division, which is an integer. Note that
                # '1//3=0'.
                result = cast(int, left_value) // cast(int, right_value)
            case _:  # pragma: no cover
                # In the scanner I've already filtered out anything that could
                # be a problem, but the type checkers require something here.
                pass  # pragma: no cover

        binary.value = result
        return binary

    def visit_group_expression(self: Interpreter, group: Group) -> LanguageItem:
        """Process a grouped expression."""
        result: LanguageItem = self._evaluate(group.expression)
        group.value = result.value
        return group

    def visit_random_expression(self: Interpreter, random: Random) -> LanguageItem:
        """Process a RND expression."""
        # What's the expression value?
        result: LanguageItem = self._evaluate(random.expression)
        value = result.value

        if (int_value := cast(int, value)) == 0:
            self._raise_error(
                random.line,
                random.column,
                "Error: #259 RND(0) not allowed.",
            )

        int_value = randbelow(int_value)

        random.value = int_value

        return random

    # The two "callable" routines tbp supports with the USR function.
    READ_ROUTINE = 276
    WRITE_ROUTINE = 280

    # The byte range so we can check if we are accidentally going past the byte
    # size.
    MIN_BYTE = 0
    MAX_BYTE = 256

    # The total size of the original Tiny BASIC address space.
    MEM_SIZE = 65536

    def visit_usr_expression(self: Interpreter, usr: Usr) -> LanguageItem:
        """Process a USR expression."""
        # The first thing is to check the routine being requested. We only
        # support the read (276) and write (280) subroutines to USR.
        routine: LanguageItem = self._evaluate(usr.subroutine)
        if routine.value not in {self.READ_ROUTINE, self.WRITE_ROUTINE}:
            self._raise_error(
                usr.line,
                usr.column,
                "Error #360: USR only supports read (276) or write (280) "
                f"subroutines, given {routine.value}",
            )

        # In both read and write, the x_reg value, which is the address to
        # read/write cannot be None.
        if usr.x_reg is None:
            self._raise_error(
                usr.line,
                usr.column,
                "Error #361: USR read/write routines require an address in XReg.",
            )

        # We know we have the x_reg, so evaluate it to get the final address.

        # I have defined usr.x_reg to be LanguageItem | None. I guess the type
        # checker can't see that right above, I validated it is not None.
        # Something feels off about the type checking in Python when you want
        # a declaration of a type that can be empty, indicating the variable
        # isn't used, or if not None is usable. Or it's that I don't understand
        # the typing requirements.
        what_the_hell: LanguageItem = cast(LanguageItem, usr.x_reg)
        x_address: LanguageItem = self._evaluate(what_the_hell)

        # It's perfectly reasonable that the address to read or write is a
        # negative value indicating that the program wants to write at an
        # offset from the end of the address range. The life program does this.
        # However, for debugging it's hard to keep track of negative addresses
        # in my tiny brain. Here I'll convert it to a positive value.
        if (mem_address := cast(int, x_address.value)) < 0:
            mem_address = self.MEM_SIZE + mem_address

        # Writing requires the value to write in a_reg.
        if routine.value == self.WRITE_ROUTINE and usr.a_reg is None:
            self._raise_error(
                usr.line,
                usr.column,
                "Error #362: USR write routine requires a value in AReg.",
            )

        final_return_value: int = 0

        # With all the checks out of the way, we can finally do the memory
        # operation.
        if routine.value == self.WRITE_ROUTINE:
            what_the_hell_2 = cast(LanguageItem, usr.a_reg)
            val_to_write: LanguageItem = self._evaluate(what_the_hell_2)
            the_byte = cast(int, val_to_write.value)

            if (the_byte < Interpreter.MIN_BYTE) or (the_byte > Interpreter.MAX_BYTE):
                self._raise_error(
                    usr.line,
                    usr.column,
                    "Error #362: USR write routine on supports values in "
                    f"AReg between 0 and 256, given '{the_byte}'.",
                )

            self._logger.debug(
                "USR writing %d to %d",
                the_byte,
                mem_address,
            )

            val = self._mem.write_memory(mem_address, the_byte)
            final_return_value = val
        else:
            self._logger.debug("USR reading %d", mem_address)

            val = self._mem.read_memory(mem_address)
            final_return_value = val

        usr.value = final_return_value
        return usr

    def visit_goto_statement(self: Interpreter, goto: Goto) -> LanguageItem:
        """Process a GOTO statement."""
        ip_target: LanguageItem = self._evaluate(goto.target)
        if (line := cast(int, ip_target.value)) not in self._lines:
            self._raise_error(
                goto.line,
                goto.column,
                f"Error #046: GOTO subroutine does not exist '{line}'.",
            )
        self._branch_ip = line
        return cast(Goto, None)

    def visit_gosub_statement(self: Interpreter, gosub: Gosub) -> LanguageItem:
        """Process a GOSUB statement."""
        ip_target: LanguageItem = self._evaluate(gosub.target)
        if (line := cast(int, ip_target.value)) not in self._lines:
            self._raise_error(
                gosub.line,
                gosub.column,
                f"Error #046: GOSUB subroutine does not exist '{line}'.",
            )
        # Get the next line as our return address.
        if (ip_return := self._get_next_line(gosub.line)) == 0:
            self._raise_error(
                gosub.line,
                gosub.column,
                "Error #345: GOSUB return address is invalid.",
            )
        # Push the return address on the callstack.
        self._callstack.append(ip_return)

        self._branch_ip = line
        return cast(Gosub, None)

    def visit_return_statement(self: Interpreter, ret: Return) -> LanguageItem:
        """Process a RETURN statement."""
        # Is the callstack empty?
        if len(self._callstack) == 0:
            self._raise_error(
                ret.line,
                ret.column,
                "Error #133: RETURN called with an empty call stack.",
            )
        self._branch_ip = self._callstack.pop()
        return cast(Return, None)

    def visit_end_statement(self: Interpreter, end: End) -> LanguageItem:
        """Process an END statement."""
        del end
        if self._the_state == Interpreter.State.RUNNING_STATE:
            # Clean up possible RUN parameters that were not used.
            self.initialize_runtime_state()
        return cast(End, None)  # pragma: no cover

    # Some constants for line numbers.
    LOW_NUMBER: int = 1
    HIGH_NUMBER: int = 32767

    # Helper method for visit_list_statement.
    def __validate_line_numbers(self: Interpreter, *lines: int) -> bool:
        return not any(
            line < self.LOW_NUMBER or line > self.HIGH_NUMBER for line in lines
        )

    def visit_list_statement(self: Interpreter, lister: List) -> LanguageItem:
        """Process a LIST statement."""
        # What are the parameters?
        low_line: int = self.LOW_NUMBER
        high_line: int = self.HIGH_NUMBER

        if lister.start_line is not None:
            param: LanguageItem = self._evaluate(lister.start_line)
            low_line = cast(int, param.value)

        if lister.end_line is not None:
            param2: LanguageItem = self._evaluate(lister.end_line)
            high_line = cast(int, param2.value)

        # Do the sanity checks.
        if low_line >= high_line:
            self._raise_error(
                lister.line,
                lister.column,
                "Error #337: LIST parameters must be in logical order, not "
                f"'{low_line}','{high_line}'.",
            )

        if self.__validate_line_numbers(low_line, high_line) is False:
            self._raise_error(
                lister.line,
                lister.column,
                "Error #338: LIST parameters must be in the range 1 to 32767 "
                f"not '{low_line}, {high_line}'.",
            )

        # Do we have just a first parameter?
        if ((low_line != self.LOW_NUMBER) and (high_line == self.HIGH_NUMBER)) and (
            low_line in self._lines
        ):
            print_output(f"{self._lines[low_line].source}\n")
        else:
            # It's zero or two parameters that are hopefully set right. :)
            for num in self._lines:
                # Thanks, Pylint! I'd originally had
                #  if num >= low_line and num <= high_line:
                # I didn't know Python could do this. I *LOVE* it! How obvious!
                if low_line <= num <= high_line:
                    print_output(f"{self._lines[num].source}\n")

        return cast(List, None)

    def visit_if_statement(self: Interpreter, if_stmt: If) -> LanguageItem:
        """Process an IF statement."""
        # The first step is to evaluate both sides of the relational operation.
        lhs: LanguageItem = self._evaluate(if_stmt.lhs)
        rhs: LanguageItem = self._evaluate(if_stmt.rhs)

        lhs_value: int = cast(int, lhs.value)
        rhs_value: int = cast(int, rhs.value)

        result: bool = False
        # Based on the relational operator, do the deed.
        match if_stmt.operator.tbp_type:
            case TokenType.EQUAL:
                result = lhs_value == rhs_value
            case TokenType.NOT_EQUAL:
                result = lhs_value != rhs_value
            case TokenType.LESS:
                result = lhs_value < rhs_value
            case TokenType.LESS_EQUAL:
                result = lhs_value <= rhs_value
            case TokenType.GREATER:
                result = lhs_value > rhs_value
            case TokenType.GREATER_EQUAL:
                result = lhs_value >= rhs_value
            case _:  # pragma: no cover
                pass  # pragma: no cover

        # If the result of the comparison is True, we need to branch.
        if result is True:
            self._evaluate(if_stmt.branch)
        return cast(If, None)

    def visit_clear_statement(self: Interpreter, clear: Clear) -> LanguageItem:
        """Process a CLEAR statement."""
        del clear
        # That was difficult.
        self.initialize_runtime_state()
        self.clear_program()
        return cast(Clear, None)

    def visit_run_statement(self: Interpreter, run_stmt: Run) -> LanguageItem:
        """Process a RUN statement."""
        if self._the_state != Interpreter.State.RUNNING_STATE:
            # Direct execution for the win.
            # Is there a program loaded?
            if len(self._lines) == 0:
                print_output("Error #013: No program in memory to run.\n")
            else:
                # Save off any parameters passed to the direct execution RUN.
                self._run_params = run_stmt.input_values[:]
                # Reverse the list so I can treat it like a stack in the INPUT
                # processing.
                self._run_params.reverse()
                # Sqwee! We are executing a program!
                self._run_program()
        else:
            # The program is running and we've encountered a program line that
            # has a RUN statement on it. Like '110 RUN', which is perfectly
            # legal. This restarts the app.
            self.initialize_runtime_state()
            self._run_program()
        return cast(Run, None)

    ###########################################################################
    # PRIVATE: INPUT handling methods.
    ###########################################################################

    @staticmethod
    def _build_input_prompt(
        index_start: int,
        var_list: list[Variable],
    ) -> str:
        """Build the input prompt for the variables."""
        prompt_text: str = "["

        list_len = len(var_list)
        curr_index = index_start
        while curr_index < list_len:
            prompt_text += f"{var_list[curr_index].name}"
            curr_index += 1
            if curr_index < list_len:
                prompt_text += ","

        prompt_text += "]? "
        return prompt_text.upper()

    def _assign_input_expression(
        self: Interpreter,
        var_name: str,
        var_value: str,
    ) -> bool:
        """Set the specific variable the value the user entered."""
        return_value: bool = True
        var_name = var_name.upper()
        try:
            fake_let = f"LET {var_name}={var_value}"
            lex_tokens = self._scanner.scan_tokens(fake_let)
            tokens = self._parser.parse_tokens(lex_tokens)
            for token in tokens:
                self._evaluate(token)
        except TbpBaseError:
            # The rhs value is invalid.
            return_value = False
            msg = (
                f"Error #351: Invalid value in INPUT: '{var_value}'. Setting "
                f"'{var_name}=0' as default.\n"
            )
            print_output(msg)
            self._assign_input_expression(var_name, "0")

        return return_value

    def visit_input_statement(
        self: Interpreter,
        input_stmt: Input,
    ) -> LanguageItem:
        """Process an INPUT statement."""
        curr_index: int = 0
        list_len: int = len(input_stmt.variables)

        while curr_index < list_len:
            # Are there any run parameters we need to process?
            if len(self._run_params) > 0:
                while (curr_index < list_len) and (len(self._run_params) > 0):
                    param = self._run_params.pop()
                    try:
                        p_value = self._evaluate(param)
                        self._assign_input_expression(
                            input_stmt.variables[curr_index].name,
                            str(p_value.value),
                        )
                        curr_index += 1
                    except TbpBaseError as err:
                        # There was a problem in _evaluate.
                        msg = f"{err.friendly_name}: {err.message}\n"
                        print_output(msg)
                        self.initialize_runtime_state()
                        return cast(Input, None)
            else:
                # Build up the prompt.
                prompt_text = self._build_input_prompt(curr_index, input_stmt.variables)
                # Ask the user for input.
                input_good, raw_text = read_input(prompt_text)
                if input_good is False:
                    # Indicate to the rest of the interpreter that the user hit
                    # CTRL+C or CTRL+D.
                    self.initialize_runtime_state()
                    print_output("Error #350: Aborting RUN from INPUT entry.\n")
                    return cast(Input, None)

                # Split the input string on commas.
                raw_list = raw_text.split(",")
                raw_len = len(raw_list)
                raw_index = 0
                while (curr_index < list_len) and (raw_index < raw_len):
                    # As the input can be a number, a variable, or any sort of
                    # expression, I'm going to treat this as a LET so
                    # everything is evaluated in the correct context.
                    self._assign_input_expression(
                        input_stmt.variables[curr_index].name,
                        raw_list[raw_index],
                    )
                    curr_index += 1
                    raw_index += 1

                if raw_index < raw_len:
                    print_output(
                        "WARN #001: More input given than variables requested "
                        "by INPUT.\n",
                    )

        return cast(Input, None)
