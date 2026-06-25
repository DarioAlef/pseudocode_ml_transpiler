"""Testes unitarios de mapeamento de builtins matematicos do emissor (T004, US1, US3).

Cobre:
  - Mapeamento essenciais (raiz, potencia, logaritmo, exp, absoluto) (FR-001, FR-002, FR-009)
  - Mapeamento adicionais (seno, cosseno, piso, teto, arredondar, minimo, maximo) (FR-004)
  - Aninhamento de chamadas
  - Imports seletivos (FR-005)
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from ast_nodes import (  # noqa: E402
    BlockNode,
    CallExprNode,
    FunctionNode,
    LiteralNode,
    ProgramNode,
)
from emissor import emitir  # noqa: E402


def _programa_com_call(nome_builtin, args=None):
    """Programa com funcao inicio que chama `nome_builtin(args)`."""
    call = CallExprNode(
        callee=LiteralNode(kind="ident", value=nome_builtin),
        args=args or [],
    )
    inicio = FunctionNode(
        nome="inicio",
        tipo_retorno=None,
        params=[],
        body=BlockNode(stmts=[call]),
    )
    return ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")


class MapeamentoEssenciaisTest(unittest.TestCase):
    """Testes de mapeamento das funcoes essenciais (US1)."""

    def test_raiz_mapeia_para_math_sqrt(self):
        prog = _programa_com_call("raiz", [LiteralNode(kind="int", value="16")])
        py = emitir(prog)
        self.assertIn("math.sqrt(16)", py)
        self.assertIn("import math", py)

    def test_potencia_mapeia_para_math_pow(self):
        prog = _programa_com_call(
            "potencia",
            [LiteralNode(kind="int", value="2"), LiteralNode(kind="int", value="3")],
        )
        py = emitir(prog)
        self.assertIn("math.pow(2, 3)", py)
        self.assertIn("import math", py)

    def test_logaritmo_mapeia_para_math_log(self):
        prog = _programa_com_call("logaritmo", [LiteralNode(kind="int", value="1")])
        py = emitir(prog)
        self.assertIn("math.log(1)", py)
        self.assertIn("import math", py)

    def test_exp_mapeia_para_math_exp(self):
        prog = _programa_com_call("exp", [LiteralNode(kind="int", value="0")])
        py = emitir(prog)
        self.assertIn("math.exp(0)", py)
        self.assertIn("import math", py)

    def test_absoluto_mapeia_para_abs(self):
        prog = _programa_com_call("absoluto", [LiteralNode(kind="int", value="-5")])
        py = emitir(prog)
        self.assertIn("abs(-5)", py)
        self.assertNotIn("import math", py)


class MapeamentoAdicionaisTest(unittest.TestCase):
    """Testes de mapeamento das funcoes adicionais (US3)."""

    def test_seno_mapeia_para_math_sin(self):
        prog = _programa_com_call("seno", [LiteralNode(kind="int", value="0")])
        py = emitir(prog)
        self.assertIn("math.sin(0)", py)
        self.assertIn("import math", py)

    def test_cosseno_mapeia_para_math_cos(self):
        prog = _programa_com_call("cosseno", [LiteralNode(kind="int", value="0")])
        py = emitir(prog)
        self.assertIn("math.cos(0)", py)
        self.assertIn("import math", py)

    def test_piso_mapeia_para_math_floor(self):
        prog = _programa_com_call("piso", [LiteralNode(kind="real", value="2.7")])
        py = emitir(prog)
        self.assertIn("math.floor(2.7)", py)
        self.assertIn("import math", py)

    def test_teto_mapeia_para_math_ceil(self):
        prog = _programa_com_call("teto", [LiteralNode(kind="real", value="2.1")])
        py = emitir(prog)
        self.assertIn("math.ceil(2.1)", py)
        self.assertIn("import math", py)

    def test_arredondar_mapeia_para_round(self):
        prog = _programa_com_call("arredondar", [LiteralNode(kind="real", value="2.5")])
        py = emitir(prog)
        self.assertIn("round(2.5)", py)
        self.assertNotIn("import math", py)

    def test_minimo_mapeia_para_min(self):
        prog = _programa_com_call(
            "minimo",
            [LiteralNode(kind="int", value="3"), LiteralNode(kind="int", value="7")],
        )
        py = emitir(prog)
        self.assertIn("min(3, 7)", py)
        self.assertNotIn("import math", py)

    def test_maximo_mapeia_para_max(self):
        prog = _programa_com_call(
            "maximo",
            [LiteralNode(kind="int", value="3"), LiteralNode(kind="int", value="7")],
        )
        py = emitir(prog)
        self.assertIn("max(3, 7)", py)
        self.assertNotIn("import math", py)


class AninhamentoTest(unittest.TestCase):
    """Testes de aninhamento de chamadas builtins."""

    def test_raiz_potencia_aninhada(self):
        potencia_call = CallExprNode(
            callee=LiteralNode(kind="ident", value="potencia"),
            args=[LiteralNode(kind="ident", value="x"), LiteralNode(kind="int", value="2")],
        )
        raiz_call = CallExprNode(
            callee=LiteralNode(kind="ident", value="raiz"),
            args=[potencia_call],
        )
        inicio = FunctionNode(
            nome="inicio",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[raiz_call]),
        )
        prog = ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertIn("math.sqrt(math.pow(x, 2))", py)


if __name__ == "__main__":
    unittest.main()
