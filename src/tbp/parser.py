"""The parser for Tiny BASIC in Python."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################
from __future__ import annotations

from typing import cast

from tbp.errors import TbpSyntaxError
from tbp.helpers import print_output, tbp_logger
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
    Literal,
    Print,
    PrintSeparator,
    Random,
    RemComment,
    Return,
    Run,
    String,
    Unary,
    Usr,
    Variable,
)
from tbp.tokens import Token, TokenType, tokens_to_string


class Parser:
    """
    The parser for Tiny BASIC in Python.

    This parser is designed to parse a single line of Tiny BASIC code.
    """

    def __init__(self: Parser) -> None:
        """Initialize the parser class."""
        # The logger.
        self._logger = tbp_logger()

        # The current position in the lexical token list.
        self._current_token: int = 0
        # The tokens being parsed.
        self._tokens: list[Token] = []
        self._token_len = 0
        # The line number being parsed. Zero indicates direct execution.
        self._line_number = 0

    def parse_tokens(self: Parser, tokens: list[Token]) -> list[LanguageItem]:
        """
        Parse the tokens and return a list of statements to execute.

        The last token in tokens is required to be the sentinel token CRLF.

        Parameter
        ---------
        tokens
            The list of tokens from the scanner.

        Returns
        -------
            The list of parsed statements.

        Exceptions
        ----------
            TbpSyntaxError indicates syntax a error.

        """
        # Initialize the state variables as an instance can be called over
        # and over.
        self._tokens = tokens
        self._token_len = len(tokens)
        self._current_token = 0
        self._line_number = 0
        # The statements returned by this method.
        statements: list[LanguageItem] = []

        # Dump the tokens so we can compare them.
        self._logger.debug("%s", tokens_to_string(tokens))

        while not self._is_at_end():
            # Let us recurse.
            statement: LanguageItem = self._line()
            statements.append(statement)

        return statements

    ###########################################################################
    # Recursive descent methods.
    ###########################################################################
    MAX_LINE_NUMBER: int = 32767

    def _line(self: Parser) -> LanguageItem:
        """Parse a <line>."""
        # Is there a line number at the beginning of this line?
        current: Token = self._tokens[self._current_token]
        if self._match(TokenType.LINE_NUMBER):
            # Do this assignment before the check so the line number is set for
            # the error code in case this number is out of range.
            self._line_number = current.line
            # A little sanity check on the line number range.
            if (current.line <= 0) or (current.line > self.MAX_LINE_NUMBER):
                self._report_error(
                    f"Error #009: Line number '{current.line}' not allowed.",
                )
            return LineNumber(current.line, current.column, current.line)
        return self._statement()

    # TODO@John-Robbins: Is the dictionary of method pointers the way to go?
    # Doing this lookup with a bunch of if statements or case statements will
    # yield a high McCabe complexity number.
    # pylint: disable=too-complex, too-many-branches
    def _statement(self: Parser) -> LanguageItem:
        """Parse a statement on the line."""
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.REM):
            return self._rem_statement()
        if self._match(TokenType.LET):
            return self._let_statement()
        if self._match(TokenType.GOTO):
            return self._go_statement(TokenType.GOTO)
        if self._match(TokenType.GOSUB):
            return self._go_statement(TokenType.GOSUB)
        if self._match(TokenType.RETURN):
            # Make sure nothing else is on the line.
            self._verify_line_finished()
            return Return(self._previous().line, self._previous().column)
        if self._match(TokenType.END):
            # Make sure nothing else is on the line.
            self._verify_line_finished()
            return End(self._previous().line, self._previous().column)
        if self._match(TokenType.LIST):
            return self._list_statement()
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.CLEAR):
            # Make sure nothing else is on the line.
            self._verify_line_finished()
            return Clear(self._previous().line, self._previous().column)
        if self._match(TokenType.INPUT):
            return self._input_statement()
        if self._match(TokenType.RUN):
            return self._run_statement()

        # Is this a 'LET'-less assignment?
        if self._check(TokenType.IDENTIFIER) is True:
            return self._let_statement()

        expression: LanguageItem = self._expression()
        return expression

    def _expression(self: Parser) -> LanguageItem:
        """Parse a statement from the line."""
        expression: LanguageItem = self._term()

        return expression

    def _term(self: Parser) -> LanguageItem:
        """Parse an 'A+C'' from the line."""
        expression: LanguageItem = self._factor()
        # Notice the while here instead of if. This allows us to parse chains
        # of addition and subtraction: A+10+B+Q.
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator: Token = self._previous()
            rhs = self._factor()
            expression = Binary(
                operator.line,
                operator.column,
                expression,
                operator,
                rhs,
            )

        return expression

    def _factor(self: Parser) -> LanguageItem:
        """Parse a `A*D` from the line."""
        expression: LanguageItem = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            operator: Token = self._previous()
            rhs: LanguageItem = self._unary()
            expression = Binary(
                operator.line,
                operator.column,
                expression,
                operator,
                rhs,
            )

        return expression

    def _unary(self: Parser) -> LanguageItem:
        """Parse a unary expression: -A, +C."""
        if self._match(TokenType.PLUS, TokenType.MINUS):
            operator: Token = self._previous()
            rhs: LanguageItem = self._unary()
            return Unary(operator.line, operator.column, operator, rhs)
        expression: LanguageItem = self._primary()
        return expression

    def _primary(self: Parser) -> LanguageItem:
        """Parse the terminals from the line."""
        curr_token: Token = self._peek()
        if self._match(TokenType.NUMBER):
            return Literal(
                curr_token.line,
                curr_token.column,
                cast(int, curr_token.value),
            )
        if self._match(TokenType.IDENTIFIER):
            return Variable(curr_token.line, curr_token.column, curr_token.lexeme)
        if self._match(TokenType.RND):
            return self._random_expression()
        if self._match(TokenType.USR):
            return self._usr_expression()
        if self._match(TokenType.COMMA, TokenType.SEMICOLON):
            return PrintSeparator(curr_token.line, curr_token.column, curr_token.lexeme)
        if self._match(TokenType.LEFT_PAREN):
            expression: LanguageItem = self._expression()
            self._consume(
                TokenType.RIGHT_PAREN,
                (
                    "Error #296: Syntax error - expected a "
                    f"closing parenthesis, got '{self._peek().lexeme!s}."
                ),
            )
            return Group(curr_token.line, curr_token.column, expression)

        # If we get here, we have a problem.
        self._report_error(
            "Error #293: Syntax error - "
            f"unexpected expression '{self._peek().lexeme!s}'.",
        )
        return cast(LanguageItem, None)  # pragma: no cover

    def _random_expression(self: Parser) -> LanguageItem:
        # This is simple!
        previous = self._previous()
        self._consume(
            TokenType.LEFT_PAREN,
            "Error #293: Syntax error - missing left parenthesis to "
            "the RND function.",
        )
        # Hoover up the expression.
        expression: LanguageItem = self._expression()
        # Match that trailing parenthesis.
        self._consume(
            TokenType.RIGHT_PAREN,
            "Error #293: Syntax error - missing left parenthesis to "
            "the RND function.",
        )
        return Random(previous.line, previous.column, expression)

    def _usr_expression(self: Parser) -> LanguageItem:
        self._consume(
            TokenType.LEFT_PAREN,
            "Error #293: Syntax error - missing left parenthesis to "
            "the USR function.",
        )
        previous = self._previous()
        # Grab the required address.
        address: LanguageItem = self._expression()
        x_reg: LanguageItem | None = None
        a_reg: LanguageItem | None = None

        # Now check for the internal arguments.
        if self._match(TokenType.COMMA):
            # This is the x_reg parameter.
            x_reg = self._expression()

            # Is the a_reg there?
            if self._match(TokenType.COMMA):
                a_reg = self._expression()

        # Match the trailing parenthesis.
        self._consume(
            TokenType.RIGHT_PAREN,
            "Error #293: Syntax error - missing right parenthesis to "
            "the USR function.",
        )
        return Usr(previous.line, previous.column, address, x_reg=x_reg, a_reg=a_reg)

    ###########################################################################
    # Statement Processing
    ###########################################################################

    def _print_statement(self: Parser) -> LanguageItem:
        """Create a print statement with it's expression."""
        previous = self._previous()
        args: list[LanguageItem] = []
        curr_token: Token = self._peek()
        # Handle the easy case where this is just a PRINT statement, which just
        # prints a CRLF.
        if curr_token.tbp_type == TokenType.CRLF:
            # We need to eat the CRLF as we just accounted for it.
            self._advance()
            return Print(previous.line, previous.column, args)

        # Do a little error checking. The in hint here was from Ruff. Thanks!
        if curr_token.tbp_type in {
            TokenType.COMMA,
            TokenType.SEMICOLON,
            TokenType.COLON,
        }:
            self._report_error(
                "Error #339: Separators or colons cannot be the first item "
                "in a PRINT statement.",
            )

        while curr_token.tbp_type not in {TokenType.CRLF, TokenType.COLON}:
            value: LanguageItem
            if self._match(TokenType.STRING):
                value = String(
                    curr_token.line,
                    curr_token.column,
                    cast(str, curr_token.value),
                )
            else:
                value = self._expression()
            args.append(value)
            curr_token = self._peek()

        # A colon can appear at the end of the PRINT, which is useful for
        # preparing data tapes because the colon will issue an "X-OFF" control
        # character. I'll just eat the colon here. Yeah, like anyone is going
        # to be pulling out their cassette tapes of Altair Tiny Basic from
        # 1976, restoring a cassette tape reader, and directly running the
        # program in tbp. A boy can dream, right? 😹
        self._match(TokenType.COLON)

        # Make sure nothing else is on the line.
        self._verify_line_finished()

        return Print(previous.line, previous.column, args)

    def _rem_statement(self: Parser) -> LanguageItem:
        # In Tiny BASIC, "REM", "REM blah", "111 REM", and "111 REM blah" are
        # all valid statements. I'll peek to see if the next token is a
        # COMMENT, and if it is, I'll add it to the REM statement.
        previous = self._previous()
        comment_text: str = ""
        if self._peek().tbp_type == TokenType.COMMENT:
            comment_token: Token = self._advance()
            comment_text = str(comment_token.value)

        # Make sure nothing else is on the line.
        self._verify_line_finished()

        return RemComment(previous.line, previous.column, comment_text)

    def _let_statement(self: Parser) -> LanguageItem:
        # We have an assignment: IDENTIFIER '=' expression.
        # First let's be smart about reporting some errors. If the line ends
        # with LET, this check gives a better error message.
        previous = self._previous()
        if self._peek().tbp_type == TokenType.CRLF:
            self._report_error(
                "Error #018: LET is missing a variable name but "
                f"found '{self._peek().lexeme!s}'.",
            )

        var_token: Token = self._consume(
            TokenType.IDENTIFIER,
            "Error #018: LET is missing a variable name but "
            f"found '{self._peek().lexeme!s}'.",
        )
        self._consume(
            TokenType.EQUAL,
            f"Error #020: LET is missing an '=' but found '{self._peek().lexeme!s}'.",
        )

        # Check that we don't have something like 'LET A='.
        if self._peek().tbp_type == TokenType.CRLF:
            self._report_error(
                "Error #023: Improper syntax in LET, no right-side expression.",
            )

        value: LanguageItem = self._expression()

        # We have all the pieces, so build it.
        var: Variable = Variable(var_token.line, var_token.column, var_token.lexeme)
        assign: Assignment = Assignment(previous.line, previous.column, var, value)

        # Make sure nothing else is on the line.
        self._verify_line_finished()

        return Let(previous.line, previous.column, assign)

    def _go_statement(self: Parser, token: TokenType) -> LanguageItem:
        previous = self._previous()
        cmd_name: str = "GOSUB"
        if token == TokenType.GOTO:
            cmd_name = "GOTO"

        first: Token = self._peek()
        # Make sure we have an expression to parse.
        if first.tbp_type == TokenType.CRLF:
            self._report_error(f"Error #037: Missing line number for '{cmd_name}'.")

        expression: LanguageItem = self._expression()

        # Make sure nothing else is on the line.
        self._verify_line_finished()

        if token == TokenType.GOTO:
            return Goto(previous.line, previous.column, expression)
        return Gosub(previous.line, previous.column, expression)

    def _list_statement(self: Parser) -> LanguageItem:
        previous = self._previous()
        start: LanguageItem = cast(LanguageItem, None)
        end: LanguageItem = cast(LanguageItem, None)

        # If the next token is the CRLF, there's no parameters to LIST.
        if self._peek().tbp_type != TokenType.CRLF:
            # We have at least one parameter for the start line.
            start = self._expression()
            # If the next token is not a ',' we only have one parameter.
            if self._peek().tbp_type == TokenType.COMMA:
                # The current token is the comma so move past it.
                self._advance()
                end = self._expression()

        # Make sure nothing else is on the line.
        self._verify_line_finished()

        return List(previous.line, previous.column, start, end)

    def _if_statement(self: Parser) -> LanguageItem:
        previous = self._previous()
        # Grab the lhs expression.
        lhs: LanguageItem = self._expression()

        # Save the operator.
        operator: Token = self._peek()
        if (
            self._match(
                TokenType.EQUAL,
                TokenType.NOT_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
            )
            is False
        ):
            self._report_error(
                (
                    "Error #330: IF is missing the relational operator but "
                    f"found '{operator.lexeme!s}'."
                ),
            )

        rhs: LanguageItem = self._expression()

        # Is the next statement the optional' THEN'? If so, match it and move
        # on.
        self._match(TokenType.THEN)

        # Now we have the branch statement.
        branch: LanguageItem = self._statement()

        # Verify nothing else is on the line.
        self._verify_line_finished()

        return If(previous.line, previous.column, lhs, operator, rhs, branch)

    def _clear_statement(self: Parser) -> LanguageItem:
        current = self._previous()
        self._verify_line_finished()
        return Clear(current.line, current.column)

    def _input_statement(self: Parser) -> LanguageItem:
        previous = self._previous()
        curr_var: Token = self._peek()
        # Make sure we have an expression to parse.
        if curr_var.tbp_type == TokenType.CRLF:
            self._report_error(
                "Error #104: INPUT expected a variable name but found '\n'.",
            )

        variables: list[Variable] = []

        # I guess you could have all 26 letters as parameters to INPUT.

        # Do a sanity check.
        if curr_var.tbp_type != TokenType.IDENTIFIER:
            self._report_error(
                "Error #104: INPUT expected a variable name but found "
                f" '{curr_var.lexeme!s}'.",
            )
        while self._match(TokenType.IDENTIFIER):
            # Create the variable.
            variables.append(Variable(curr_var.line, curr_var.column, curr_var.lexeme))
            # Eat the comma if it is there.
            if self._match(TokenType.COMMA):
                # Grab the next potential variable.
                curr_var = self._peek()
                if curr_var.tbp_type != TokenType.IDENTIFIER:
                    self._report_error(
                        "Error #104: INPUT expected a variable name but found "
                        f" '{curr_var.lexeme!s}'.",
                    )
            else:
                # No comma after the variable, so end this loop.
                break

        # Verify nothing else is on the line.
        self._verify_line_finished()

        return Input(previous.line, previous.column, variables)

    def _run_statement(self: Parser) -> LanguageItem:
        previous = self._previous()
        # See the tbp documentation because RUN is a different than the
        # documentation.
        expressions: list[LanguageItem] = []

        if self._peek().tbp_type == TokenType.CRLF:
            # We need to eat the CRLF as we just accounted for it.
            self._advance()
            return Run(previous.line, previous.column, expressions)

        # Does this happen to be the elusive "100 RUN a,b,10" inside a program
        # line? If so, ignore everything after the RUN.
        if self._line_number > 0:
            self._report_warning(
                "WARN #002: RUN parameters not supported in programs, only in "
                f"direct execution: Line [{self._line_number}].",
            )
            while self._peek().tbp_type != TokenType.CRLF:
                self._advance()
            return Run(previous.line, previous.column, expressions)

        # It's direct execution and there are parameters.
        while self._peek().tbp_type != TokenType.CRLF:
            if self._peek().tbp_type == TokenType.COMMA:
                # Eat the comma.
                self._advance()
                # Could this be an extraneous, trailing comma?
                if self._is_at_end() is True:
                    self._report_error("Error #296: Syntax error")
                continue
            curr_expression: LanguageItem = self._expression()
            expressions.append(curr_expression)

        return Run(previous.line, previous.column, expressions)

    ###########################################################################
    # Token position changing and checking methods.
    ###########################################################################

    def _peek(self: Parser) -> Token:
        """Return the current token from the token stream."""
        return self._tokens[self._current_token]

    def _previous(self: Parser) -> Token:
        """Return the previous token from the token stream."""
        return self._tokens[self._current_token - 1]

    def _advance(self: Parser) -> Token:
        """Get the next token to process."""
        if self._is_at_end() is False:
            self._current_token += 1
        return self._previous()

    def _is_at_end(self: Parser) -> bool:
        """Check if we are at the end of the token stream."""
        return self._current_token == (self._token_len - 1)

    ###########################################################################
    # Token matching methods.
    ###########################################################################

    def _match(self: Parser, *types: TokenType) -> bool:
        """Check to see if the next token(s) is match the list passed in."""
        for token_type in types:
            if self._check(token_type) is True:
                self._advance()
                return True
        return False

    def _consume(self: Parser, token_type: TokenType, message: str) -> Token:
        """Check if the next token is what is expected."""
        if self._check(token_type) is True:
            return self._advance()

        # We have a syntax error
        self._report_error(message)
        # Keep mypy and Ruff quiet.
        return Token(TokenType.CRLF, "", 0, 0, 0)  # pragma: no cover

    def _check(self: Parser, token_type: TokenType) -> bool:
        """Check if the current token is one we are looking for."""
        if self._is_at_end() is True:
            return False
        return self._peek().tbp_type == token_type

    def _verify_line_finished(self: Parser) -> None:
        """All the statements have to be the last thing on the line."""
        curr_token: Token = self._peek()
        if curr_token.tbp_type == TokenType.CRLF:
            return
        self._report_error(
            f"Expected the end of the line but found {self._peek().lexeme!r}.",
        )

    def _report_error(self: Parser, message: str) -> None:
        """Raise the error for the interpreter/compiler."""
        token: Token = self._peek()
        error: TbpSyntaxError = TbpSyntaxError(token.line, token.column, message)
        raise error

    @staticmethod
    def _report_warning(message: str) -> None:
        print_output(f"{message}\n")
