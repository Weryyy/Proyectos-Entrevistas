"""
Módulo 10: Mini Compilador — Lexer (Analizador Léxico).

Convierte código fuente (string) en una secuencia de Tokens.
No usa librerías externas — solo la biblioteca estándar de Python.

Lore: Eres el constructor del lenguaje de programación para una civilización
de robots. El lexer es el primer paso: romper el texto en palabras con significado.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Literales
    NUMBER = auto()      # 42  o  3.14
    BOOLEAN = auto()     # true / false
    IDENTIFIER = auto()  # nombre de variable
    # Operadores aritméticos
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    # Operadores de comparación
    ASSIGN = auto()      # =
    EQUAL = auto()       # ==
    NOT_EQUAL = auto()   # !=
    LESS = auto()        # <
    GREATER = auto()     # >
    LESS_EQ = auto()     # <=
    GREATER_EQ = auto()  # >=
    # Delimitadores
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    COMMA = auto()       # ,
    NEWLINE = auto()     # \n
    # Palabras clave
    LET = auto()
    IF = auto()
    ELSE = auto()
    PRINT = auto()
    # Especial
    EOF = auto()


KEYWORDS = {
    'let':   TokenType.LET,
    'if':    TokenType.IF,
    'else':  TokenType.ELSE,
    'print': TokenType.PRINT,
    'true':  TokenType.BOOLEAN,
    'false': TokenType.BOOLEAN,
}


@dataclass
class Token:
    type: TokenType
    value: object  # int | float | bool | str | None
    line: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, línea={self.line})"


class LexerError(Exception):
    """Error durante el análisis léxico."""


class Lexer:
    """
    Analizador léxico: convierte código fuente en tokens.

    Uso:
        lexer = Lexer("let x = 42")
        tokens = lexer.tokenize()
    """

    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1

    def _current(self) -> Optional[str]:
        return self.source[self.pos] if self.pos < len(self.source) else None

    def _peek(self, offset: int = 1) -> Optional[str]:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else None

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def _skip_whitespace(self) -> None:
        while self._current() in (' ', '\t', '\r'):
            self._advance()

    def _skip_comment(self) -> None:
        """Ignora comentarios de una sola línea que empiezan con #."""
        while self._current() is not None and self._current() != '\n':
            self._advance()

    def _read_number(self) -> Token:
        start_line = self.line
        digits: List[str] = []
        has_dot = False
        while self._current() is not None and (
            self._current().isdigit() or
            (self._current() == '.' and not has_dot and
             self._peek() is not None and self._peek().isdigit())
        ):
            if self._current() == '.':
                has_dot = True
            digits.append(self._advance())
        text = ''.join(digits)
        value: object = float(text) if has_dot else int(text)
        return Token(TokenType.NUMBER, value, start_line)

    def _read_identifier(self) -> Token:
        start_line = self.line
        chars: List[str] = []
        while self._current() is not None and (
            self._current().isalnum() or self._current() == '_'
        ):
            chars.append(self._advance())
        text = ''.join(chars)
        tok_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        if text == 'true':
            value: object = True
        elif text == 'false':
            value = False
        else:
            value = text
        return Token(tok_type, value, start_line)

    def tokenize(self) -> List[Token]:
        """
        Convierte el código fuente completo en una lista de Tokens.
        El último token siempre es EOF.
        """
        tokens: List[Token] = []
        while True:
            self._skip_whitespace()
            ch = self._current()

            if ch is None:
                tokens.append(Token(TokenType.EOF, None, self.line))
                break

            if ch == '#':
                self._skip_comment()
                continue

            if ch == '\n':
                tokens.append(Token(TokenType.NEWLINE, '\n', self.line))
                self._advance()
                continue

            if ch.isdigit() or (
                ch == '.' and self._peek() is not None and self._peek().isdigit()
            ):
                tokens.append(self._read_number())
                continue

            if ch.isalpha() or ch == '_':
                tokens.append(self._read_identifier())
                continue

            start_line = self.line
            self._advance()

            if ch == '+':
                tokens.append(Token(TokenType.PLUS, '+', start_line))
            elif ch == '-':
                tokens.append(Token(TokenType.MINUS, '-', start_line))
            elif ch == '*':
                tokens.append(Token(TokenType.STAR, '*', start_line))
            elif ch == '/':
                tokens.append(Token(TokenType.SLASH, '/', start_line))
            elif ch == '(':
                tokens.append(Token(TokenType.LPAREN, '(', start_line))
            elif ch == ')':
                tokens.append(Token(TokenType.RPAREN, ')', start_line))
            elif ch == ',':
                tokens.append(Token(TokenType.COMMA, ',', start_line))
            elif ch == '=':
                if self._current() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.EQUAL, '==', start_line))
                else:
                    tokens.append(Token(TokenType.ASSIGN, '=', start_line))
            elif ch == '!':
                if self._current() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.NOT_EQUAL, '!=', start_line))
                else:
                    raise LexerError(
                        f"Carácter inesperado '!' en línea {start_line}"
                    )
            elif ch == '<':
                if self._current() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.LESS_EQ, '<=', start_line))
                else:
                    tokens.append(Token(TokenType.LESS, '<', start_line))
            elif ch == '>':
                if self._current() == '=':
                    self._advance()
                    tokens.append(Token(TokenType.GREATER_EQ, '>=', start_line))
                else:
                    tokens.append(Token(TokenType.GREATER, '>', start_line))
            else:
                raise LexerError(
                    f"Carácter inesperado '{ch}' en línea {start_line}"
                )

        return tokens
