"""
Módulo 10: Mini Compilador — Intérprete (Evaluador de AST).

Evalúa el Árbol de Sintaxis Abstracta (AST) recorriendo sus nodos.
Usa un entorno (Environment) para gestionar variables con ámbito léxico.

Lore: El intérprete es el procesador central del robot — toma el AST
y lo ejecuta instrucción por instrucción para dar vida al programa.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from lexer import Lexer
from parser import (
    Assign, BinaryOp, Boolean, Float, If, Number,
    Parser, Print, Program, UnaryOp, Variable,
)


# ─────────────────────────────────────────────────────────────────────────────
# Excepciones semánticas
# ─────────────────────────────────────────────────────────────────────────────

class InterpreterError(Exception):
    """Error genérico del intérprete."""

class DivisionPorCero(InterpreterError):
    """División por cero detectada en tiempo de ejecución."""

class VariableNoDefinida(InterpreterError):
    """Se intentó leer una variable que no existe en ningún ámbito."""

class ErrorDeTipo(InterpreterError):
    """Operación aplicada a tipos incompatibles."""


# ─────────────────────────────────────────────────────────────────────────────
# Entorno de variables
# ─────────────────────────────────────────────────────────────────────────────

class Environment:
    """
    Entorno de ejecución con soporte para ámbitos anidados.

    Cada bloque (if, función futura) crea un hijo con parent=entorno_actual.
    La búsqueda de variables sube por la cadena de padres.
    """

    def __init__(self, parent: Optional[Environment] = None) -> None:
        self._vars: Dict[str, Any] = {}
        self.parent = parent

    def get(self, name: str) -> Any:
        if name in self._vars:
            return self._vars[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise VariableNoDefinida(f"Variable '{name}' no definida")

    def set(self, name: str, value: Any) -> None:
        self._vars[name] = value

    def has(self, name: str) -> bool:
        if name in self._vars:
            return True
        return self.parent is not None and self.parent.has(name)


# ─────────────────────────────────────────────────────────────────────────────
# Intérprete principal
# ─────────────────────────────────────────────────────────────────────────────

class Interpreter:
    """
    Intérprete de árbol (tree-walking interpreter).

    Recorre el AST de forma recursiva evaluando cada nodo.
    Las variables globales persisten entre llamadas a run().
    La lista output captura todo lo impreso por print().

    Uso básico:
        interp = Interpreter()
        interp.run("let x = 10")
        interp.run("print(x + 5)")  # imprime 15
        print(interp.output)        # ['15']
    """

    def __init__(self) -> None:
        self.global_env = Environment()
        self.output: List[str] = []

    # ── Evaluación principal ───────────────────────────────────────────────────

    def evaluate(self, node: Any, env: Optional[Environment] = None) -> Any:
        """Evalúa un nodo AST y devuelve su valor."""
        if env is None:
            env = self.global_env

        if isinstance(node, Program):
            result = None
            for stmt in node.statements:
                result = self.evaluate(stmt, env)
            return result

        if isinstance(node, Number):
            return node.value

        if isinstance(node, Float):
            return node.value

        if isinstance(node, Boolean):
            return node.value

        if isinstance(node, Variable):
            return env.get(node.name)

        if isinstance(node, Assign):
            value = self.evaluate(node.value, env)
            env.set(node.name, value)
            return value

        if isinstance(node, BinaryOp):
            return self._eval_binary(node, env)

        if isinstance(node, UnaryOp):
            return self._eval_unary(node, env)

        if isinstance(node, If):
            return self._eval_if(node, env)

        if isinstance(node, Print):
            return self._eval_print(node, env)

        raise InterpreterError(f"Nodo AST desconocido: {type(node).__name__}")

    # ── Evaluadores específicos ────────────────────────────────────────────────

    def _eval_binary(self, node: BinaryOp, env: Environment) -> Any:
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        op = node.op

        # Operadores aritméticos — requieren números (bool excluido: es subclase de int)
        if op in ('+', '-', '*', '/'):
            if not isinstance(left, (int, float)) or isinstance(left, bool):
                raise ErrorDeTipo(
                    f"Operador '{op}' requiere número en operando izquierdo, "
                    f"se obtuvo {type(left).__name__}"
                )
            if not isinstance(right, (int, float)) or isinstance(right, bool):
                raise ErrorDeTipo(
                    f"Operador '{op}' requiere número en operando derecho, "
                    f"se obtuvo {type(right).__name__}"
                )
            if op == '+':
                return left + right
            if op == '-':
                return left - right
            if op == '*':
                return left * right
            # op == '/'
            if right == 0:
                raise DivisionPorCero("División por cero")
            return left / right

        # Operadores de igualdad — cualquier tipo
        if op == '==':
            return left == right
        if op == '!=':
            return left != right

        # Operadores de comparación — requieren números (bool excluido)
        if op in ('<', '>', '<=', '>='):
            if (not isinstance(left, (int, float)) or isinstance(left, bool) or
                    not isinstance(right, (int, float)) or isinstance(right, bool)):
                raise ErrorDeTipo(
                    f"Operador '{op}' requiere números"
                )
            if op == '<':
                return left < right
            if op == '>':
                return left > right
            if op == '<=':
                return left <= right
            return left >= right

        raise InterpreterError(f"Operador binario desconocido: '{op}'")

    def _eval_unary(self, node: UnaryOp, env: Environment) -> Any:
        operand = self.evaluate(node.operand, env)
        if node.op == '-':
            if not isinstance(operand, (int, float)) or isinstance(operand, bool):
                raise ErrorDeTipo(
                    f"Operador unario '-' requiere número, "
                    f"se obtuvo {type(operand).__name__}"
                )
            return -operand
        raise InterpreterError(f"Operador unario desconocido: '{node.op}'")

    def _eval_if(self, node: If, env: Environment) -> Any:
        condition = self.evaluate(node.condition, env)
        body = node.then_body if condition else node.else_body
        if not body:
            return None
        child_env = Environment(parent=env)
        result = None
        for stmt in body:
            result = self.evaluate(stmt, child_env)
        return result

    def _eval_print(self, node: Print, env: Environment) -> Any:
        value = self.evaluate(node.expr, env)
        text = self._format(value)
        self.output.append(text)
        print(text)
        return value

    @staticmethod
    def _format(value: Any) -> str:
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)

    # ── Punto de entrada de alto nivel ────────────────────────────────────────

    def run(self, source: str) -> Any:
        """
        Compila y ejecuta código fuente completo.

        Las variables definidas persisten en self.global_env
        entre llamadas sucesivas. self.output se reinicia en cada llamada.
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        self.output = []
        return self.evaluate(ast)
