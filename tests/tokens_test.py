"""Unit tests for the Tokens class."""

###############################################################################
# Tiny BASIC in Python
# Licensed under the MIT License.
# Copyright (c) 2024 John Robbins
###############################################################################

from __future__ import annotations

from tbp.tokens import Token, TokenType


def test_token() -> None:
    """Basic initialization test."""
    the_token = Token(TokenType.CLEAR, "CLEAR", 1, 1)
    assert the_token.tbp_type == TokenType.CLEAR
