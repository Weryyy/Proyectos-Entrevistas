"""
Módulo 10: Mini Compilador — Parser (Analizador Sintáctico).

Construye un Árbol de Sintaxis Abstracta (AST) a partir de una lista de Tokens.
Usa un parser de descenso recursivo con precedencia de Pratt.

Precedencia (de menor a mayor):
  1. Comparación:   ==  !=  <  >  <=  >=
  2. Suma/Resta:    +  -
  3. Mult/Div:      *  /
  4. Unario:        -expr
  5. Primario:      número, bool, variable, (expresión)

Lore: El parser es el intérprete de gramática del lenguaje robot — toma los
tokens y los organiza en una estructura jerárquica con significado semántico.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List

from lexer import Lexer, Token, TokenType


# ─────────────────────────────────────────────────────────────────────────────
# Nodos del AST
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Number:
    """Literal entero: 42"""
    value: int

@dataclass
class Float:
    """Literal flotante: 3.14"""
    value: float

@dataclass
class Boolean:
    """Literal booleano: true / false"""
    value: bool

@dataclass
class Variable:
    """Referencia a variable: x"""
    name: str

@dataclass
class BinaryOp:
    """Operación binaria: left op right"""
    left: Any
    op: str
    right: Any

@dataclass
class UnaryOp:
    """Operación unaria: -expr"""
    op: str
    operand: Any

@dataclass
class Assign:
    """Asignación: let x = expr"""
    name: str
    value: Any

@dataclass
class If:
    """Condicional: if (cond) then_stmt [else else_stmt]"""
    condition: Any
    then_body: List[Any]
    else_body: List[Any] = field(default_factory=list)

@dataclass
class Print:
    """Impresión: print(expr)"""
    expr: Any

@dataclass
class Program:
    """Nodo raíz: lista de sentencias"""
    statements: List[Any]


# ─────────────────────────────────────────────────────────────────────────────
# Parser
# ─────────────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    """Error durante el análisis sintáctico."""


class Parser:
    """
    Parser de descenso recursivo para el mini-lenguaje robot.

    Gramática simplificada:
        program     → statement* EOF
        statement   → let_stmt | if_stmt | print_stmt | expression NEWLINE?
        let_stmt    → 'let' IDENTIFIER '=' expression
        if_stmt     → 'if' '(' expression ')' statement ['else' statement]
        print_stmt  → 'print' '(' expression ')'
        expression  → comparison
        comparison  → additive (('=='|'!='|'<'|'>'|'<='|'>=') additive)*
        additive    → multiplicative (('+' | '-') multiplicative)*
        multiplicative → unary (('*' | '/') unary)*
        unary       → '-' unary | primary
        primary     → NUMBER | BOOLEAN | IDENTIFIER | '(' expression ')'
    """

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _expect(self, tok_type: TokenType) -> Token:
        tok = self._current()
        if tok.type != tok_type:
            raise ParseError(
                f"Se esperaba {tok_type.name}, se encontró "
                f"{tok.type.name} ('{tok.value}') en línea {tok.line}"
            )
        return self._advance()

    def _skip_newlines(self) -> None:
        while self._current().type == TokenType.NEWLINE:
            self._advance()

    # ── Reglas de gramática ────────────────────────────────────────────────────

    def parse(self) -> Program:
        statements: List[Any] = []
        self._skip_newlines()
        while self._current().type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()
        return Program(statements)

    def _parse_statement(self) -> Any:
        tok = self._current()
        if tok.type == TokenType.LET:
            return self._parse_let()
        if tok.type == TokenType.IF:
            return self._parse_if()
        if tok.type == TokenType.PRINT:
            return self._parse_print()
        if tok.type == TokenType.NEWLINE:
            self._advance()
            return None
        return self._parse_expression()

    def _parse_let(self) -> Assign:
        self._advance()  # consume 'let'
        name_tok = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.ASSIGN)
        value = self._parse_expression()
        return Assign(name_tok.value, value)

    def _parse_if(self) -> If:
        self._advance()  # consume 'if'
        self._expect(TokenType.LPAREN)
        condition = self._parse_expression()
        self._expect(TokenType.RPAREN)
        self._skip_newlines()
        then_body = self._parse_block()
        else_body: List[Any] = []
        self._skip_newlines()
        if self._current().type == TokenType.ELSE:
            self._advance()  # consume 'else'
            self._skip_newlines()
            else_body = self._parse_block()
        return If(condition, then_body, else_body)

    def _parse_block(self) -> List[Any]:
        """Parsea un bloque de una sola sentencia."""
        self._skip_newlines()
        stmt = self._parse_statement()
        return [stmt] if stmt is not None else []

    def _parse_print(self) -> Print:
        self._advance()  # consume 'print'
        self._expect(TokenType.LPAREN)
        expr = self._parse_expression()
        self._expect(TokenType.RPAREN)
        return Print(expr)

    # ── Expresiones (precedencia ascendente) ──────────────────────────────────

    def _parse_expression(self) -> Any:
        return self._parse_comparison()

    def _parse_comparison(self) -> Any:
        left = self._parse_additive()
        while self._current().type in (
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.LESS, TokenType.GREATER,
            TokenType.LESS_EQ, TokenType.GREATER_EQ,
        ):
            op_tok = self._advance()
            right = self._parse_additive()
            left = BinaryOp(left, op_tok.value, right)
        return left

    def _parse_additive(self) -> Any:
        left = self._parse_multiplicative()
        while self._current().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._parse_multiplicative()
            left = BinaryOp(left, op_tok.value, right)
        return left

    def _parse_multiplicative(self) -> Any:
        left = self._parse_unary()
        while self._current().type in (TokenType.STAR, TokenType.SLASH):
            op_tok = self._advance()
            right = self._parse_unary()
            left = BinaryOp(left, op_tok.value, right)
        return left

    def _parse_unary(self) -> Any:
        if self._current().type == TokenType.MINUS:
            op_tok = self._advance()
            operand = self._parse_unary()
            return UnaryOp(op_tok.value, operand)
        return self._parse_primary()

    def _parse_primary(self) -> Any:
        tok = self._current()

        if tok.type == TokenType.NUMBER:
            self._advance()
            if isinstance(tok.value, float):
                return Float(tok.value)
            return Number(tok.value)

        if tok.type == TokenType.BOOLEAN:
            self._advance()
            return Boolean(tok.value)

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return Variable(tok.value)

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr

        raise ParseError(
            f"Token inesperado '{tok.value}' "
            f"(tipo: {tok.type.name}) en línea {tok.line}"
        )
