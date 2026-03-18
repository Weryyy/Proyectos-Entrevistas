"""
Tests para el Módulo 10: Mini Compilador.

Cubre el Lexer, Parser e Intérprete por separado y de forma integrada.

Ejecutar con:
    cd main/modulo-10-mini-compilador/codigo
    pytest test_interpreter.py -v
"""

import pytest

from lexer import Lexer, LexerError, Token, TokenType
from parser import (
    Assign, BinaryOp, Boolean, Float, If, Number,
    ParseError, Parser, Print, Program, Variable,
)
from interpreter import (
    DivisionPorCero, Environment, ErrorDeTipo,
    Interpreter, VariableNoDefinida,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def tokens_of(source: str):
    return Lexer(source).tokenize()


def parse(source: str) -> Program:
    toks = Lexer(source).tokenize()
    return Parser(toks).parse()


@pytest.fixture
def interp():
    return Interpreter()


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DEL LEXER
# ─────────────────────────────────────────────────────────────────────────────


class TestLexer:
    def test_numero_entero(self):
        toks = tokens_of("42")
        assert toks[0].type == TokenType.NUMBER
        assert toks[0].value == 42
        assert isinstance(toks[0].value, int)

    def test_numero_flotante(self):
        toks = tokens_of("3.14")
        assert toks[0].type == TokenType.NUMBER
        assert toks[0].value == pytest.approx(3.14)
        assert isinstance(toks[0].value, float)

    def test_operadores_aritmeticos(self):
        toks = tokens_of("+ - * /")
        tipos = [t.type for t in toks[:-1]]
        assert tipos == [
            TokenType.PLUS, TokenType.MINUS,
            TokenType.STAR, TokenType.SLASH,
        ]

    def test_operadores_comparacion(self):
        toks = tokens_of("== != < > <= >=")
        tipos = [t.type for t in toks[:-1]]
        assert tipos == [
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.LESS, TokenType.GREATER,
            TokenType.LESS_EQ, TokenType.GREATER_EQ,
        ]

    def test_asignacion_simple(self):
        toks = tokens_of("=")
        assert toks[0].type == TokenType.ASSIGN

    def test_parentesis(self):
        toks = tokens_of("()")
        assert toks[0].type == TokenType.LPAREN
        assert toks[1].type == TokenType.RPAREN

    def test_palabras_clave(self):
        toks = tokens_of("let if else print")
        assert toks[0].type == TokenType.LET
        assert toks[1].type == TokenType.IF
        assert toks[2].type == TokenType.ELSE
        assert toks[3].type == TokenType.PRINT

    def test_booleanos(self):
        toks = tokens_of("true false")
        assert toks[0].type == TokenType.BOOLEAN
        assert toks[0].value is True
        assert toks[1].type == TokenType.BOOLEAN
        assert toks[1].value is False

    def test_identificador(self):
        toks = tokens_of("variable_x")
        assert toks[0].type == TokenType.IDENTIFIER
        assert toks[0].value == "variable_x"

    def test_identificador_no_confunde_con_keyword(self):
        toks = tokens_of("letting")
        assert toks[0].type == TokenType.IDENTIFIER
        assert toks[0].value == "letting"

    def test_salto_de_linea(self):
        toks = tokens_of("x\ny")
        tipos = [t.type for t in toks]
        assert TokenType.NEWLINE in tipos

    def test_seguimiento_de_linea(self):
        toks = tokens_of("1\n2\n3")
        assert toks[0].line == 1   # "1"
        assert toks[2].line == 2   # "2"
        assert toks[4].line == 3   # "3"

    def test_ignora_comentarios(self):
        toks = tokens_of("# esto es un comentario\n42")
        # Sólo debe haber NEWLINE, NUMBER(42), EOF
        tipos = [t.type for t in toks]
        assert TokenType.NUMBER in tipos
        assert toks[-2].value == 42

    def test_ignora_espacios(self):
        toks = tokens_of("  42  ")
        assert toks[0].type == TokenType.NUMBER
        assert toks[0].value == 42

    def test_eof_siempre_al_final(self):
        toks = tokens_of("")
        assert toks[-1].type == TokenType.EOF

    def test_caracter_invalido(self):
        with pytest.raises(LexerError, match="inesperado"):
            Lexer("@").tokenize()

    def test_caracter_invalido_exclamacion(self):
        with pytest.raises(LexerError):
            Lexer("!x").tokenize()


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DEL PARSER
# ─────────────────────────────────────────────────────────────────────────────


class TestParser:
    def test_parsea_numero_entero(self):
        ast = parse("42")
        assert isinstance(ast.statements[0], Number)
        assert ast.statements[0].value == 42

    def test_parsea_numero_flotante(self):
        ast = parse("3.14")
        assert isinstance(ast.statements[0], Float)
        assert ast.statements[0].value == pytest.approx(3.14)

    def test_parsea_booleano(self):
        ast = parse("true")
        assert isinstance(ast.statements[0], Boolean)
        assert ast.statements[0].value is True

    def test_parsea_variable(self):
        ast = parse("x")
        assert isinstance(ast.statements[0], Variable)
        assert ast.statements[0].name == "x"

    def test_precedencia_multiplicacion_sobre_suma(self):
        # 1 + 2 * 3 debe parsear como 1 + (2 * 3)
        ast = parse("1 + 2 * 3")
        expr = ast.statements[0]
        assert isinstance(expr, BinaryOp)
        assert expr.op == '+'
        assert isinstance(expr.right, BinaryOp)
        assert expr.right.op == '*'

    def test_parentesis_cambia_precedencia(self):
        # (1 + 2) * 3
        ast = parse("(1 + 2) * 3")
        expr = ast.statements[0]
        assert isinstance(expr, BinaryOp)
        assert expr.op == '*'
        assert isinstance(expr.left, BinaryOp)
        assert expr.left.op == '+'

    def test_parsea_asignacion_let(self):
        ast = parse("let x = 10")
        stmt = ast.statements[0]
        assert isinstance(stmt, Assign)
        assert stmt.name == 'x'
        assert isinstance(stmt.value, Number)
        assert stmt.value.value == 10

    def test_parsea_if_simple(self):
        ast = parse("if (true) print(42)")
        stmt = ast.statements[0]
        assert isinstance(stmt, If)
        assert isinstance(stmt.condition, Boolean)
        assert isinstance(stmt.then_body[0], Print)

    def test_parsea_if_else(self):
        ast = parse("if (true) print(1) else print(2)")
        stmt = ast.statements[0]
        assert isinstance(stmt, If)
        assert len(stmt.then_body) == 1
        assert len(stmt.else_body) == 1

    def test_parsea_print(self):
        ast = parse("print(99)")
        stmt = ast.statements[0]
        assert isinstance(stmt, Print)
        assert isinstance(stmt.expr, Number)
        assert stmt.expr.value == 99

    def test_parsea_unario_menos(self):
        from parser import UnaryOp as UO
        ast = parse("-5")
        stmt = ast.statements[0]
        assert isinstance(stmt, UO)
        assert stmt.op == '-'

    def test_parsea_multiples_sentencias(self):
        src = "let a = 1\nlet b = 2"
        ast = parse(src)
        assert len(ast.statements) == 2
        assert all(isinstance(s, Assign) for s in ast.statements)

    def test_error_sintactico(self):
        with pytest.raises(ParseError):
            parse("let = 5")  # falta el nombre de variable

    def test_programa_vacio(self):
        ast = parse("")
        assert isinstance(ast, Program)
        assert ast.statements == []


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DEL INTÉRPRETE
# ─────────────────────────────────────────────────────────────────────────────


class TestInterpreter:
    def test_suma(self, interp):
        assert interp.run("2 + 3") == 5

    def test_resta(self, interp):
        assert interp.run("10 - 4") == 6

    def test_multiplicacion(self, interp):
        assert interp.run("3 * 4") == 12

    def test_division(self, interp):
        assert interp.run("10 / 4") == pytest.approx(2.5)

    def test_precedencia(self, interp):
        assert interp.run("2 + 3 * 4") == 14

    def test_parentesis(self, interp):
        assert interp.run("(2 + 3) * 4") == 20

    def test_numero_flotante(self, interp):
        assert interp.run("3.14") == pytest.approx(3.14)

    def test_unario_menos_entero(self, interp):
        assert interp.run("-5") == -5

    def test_unario_menos_float(self, interp):
        assert interp.run("-3.14") == pytest.approx(-3.14)

    def test_asignacion_variable(self, interp):
        interp.run("let x = 42")
        assert interp.global_env.get('x') == 42

    def test_variable_en_expresion(self, interp):
        interp.run("let x = 10")
        assert interp.run("x + 5") == 15

    def test_reasignacion_variable(self, interp):
        interp.run("let x = 1")
        interp.run("let x = 99")
        assert interp.global_env.get('x') == 99

    def test_comparacion_igual(self, interp):
        assert interp.run("1 == 1") is True
        assert interp.run("1 == 2") is False

    def test_comparacion_no_igual(self, interp):
        assert interp.run("1 != 2") is True
        assert interp.run("1 != 1") is False

    def test_comparacion_menor(self, interp):
        assert interp.run("1 < 2") is True
        assert interp.run("2 < 1") is False

    def test_comparacion_mayor(self, interp):
        assert interp.run("2 > 1") is True

    def test_comparacion_menor_igual(self, interp):
        assert interp.run("1 <= 1") is True
        assert interp.run("2 <= 1") is False

    def test_comparacion_mayor_igual(self, interp):
        assert interp.run("1 >= 1") is True

    def test_if_verdadero(self, interp):
        interp.run("let x = 1")
        interp.run("if (x == 1) print(99)")
        assert "99" in interp.output

    def test_if_falso_no_imprime(self, interp):
        interp.run("let x = 0")
        interp.run("if (x == 1) print(99)")
        assert interp.output == []

    def test_if_else_rama_else(self, interp):
        interp.run("let x = 0")
        interp.run("if (x == 1) print(1) else print(2)")
        assert "2" in interp.output

    def test_if_else_rama_then(self, interp):
        interp.run("let x = 1")
        interp.run("if (x == 1) print(1) else print(2)")
        assert "1" in interp.output
        assert "2" not in interp.output

    def test_print_captura_salida(self, interp):
        interp.run("print(42)")
        assert interp.output == ["42"]

    def test_print_booleano(self, interp):
        interp.run("print(true)")
        assert interp.output == ["true"]

    def test_print_flotante_entero(self, interp):
        interp.run("print(4.0)")
        assert interp.output == ["4"]

    def test_output_se_reinicia_en_cada_run(self, interp):
        interp.run("print(1)")
        interp.run("print(2)")
        assert interp.output == ["2"]  # sólo la última ejecución

    # ── Errores ────────────────────────────────────────────────────────────────

    def test_division_por_cero(self, interp):
        with pytest.raises(DivisionPorCero):
            interp.run("10 / 0")

    def test_variable_no_definida(self, interp):
        with pytest.raises(VariableNoDefinida, match="'fantasma'"):
            interp.run("fantasma")

    def test_error_de_tipo_suma(self, interp):
        interp.run("let b = true")
        with pytest.raises(ErrorDeTipo):
            interp.run("b + 1")

    def test_error_de_tipo_unario(self, interp):
        interp.run("let b = true")
        with pytest.raises(ErrorDeTipo):
            interp.run("-b")


# ─────────────────────────────────────────────────────────────────────────────
# TESTS DE INTEGRACIÓN (pipeline completo)
# ─────────────────────────────────────────────────────────────────────────────


class TestIntegracion:
    def test_fibonacci_manual(self):
        interp = Interpreter()
        programa = (
            "let a = 0\n"
            "let b = 1\n"
            "let c = a + b\n"
        )
        interp.run(programa)
        assert interp.global_env.get('c') == 1

    def test_programa_completo_suma_e_imprime(self):
        interp = Interpreter()
        programa = (
            "let x = 10\n"
            "let y = 20\n"
            "let z = x + y\n"
            "print(z)\n"
        )
        interp.run(programa)
        assert "30" in interp.output

    def test_programa_condicional(self):
        interp = Interpreter()
        interp.run("let temperatura = 35")
        interp.run("if (temperatura > 30) print(1) else print(0)")
        assert "1" in interp.output

    def test_programa_con_flotantes(self):
        interp = Interpreter()
        programa = "let pi = 3.14\nlet r = 2.0\nlet area = pi * r * r\n"
        interp.run(programa)
        assert interp.global_env.get('area') == pytest.approx(12.56)

    def test_expresion_compleja(self):
        interp = Interpreter()
        assert interp.run("(10 + 2) * (8 - 3) / 4") == pytest.approx(15.0)

    def test_variables_persisten_entre_runs(self):
        interp = Interpreter()
        interp.run("let base = 100")
        interp.run("let incremento = 50")
        assert interp.run("base + incremento") == 150

    def test_programa_con_comentarios(self):
        interp = Interpreter()
        programa = (
            "# Calcula el doble de un número\n"
            "let n = 7\n"
            "let doble = n * 2\n"
            "print(doble)\n"
        )
        interp.run(programa)
        assert "14" in interp.output
