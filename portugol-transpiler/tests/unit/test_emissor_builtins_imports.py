"""Testes unitarios de imports seletivos para builtins matematicos (T007, US2).

Cobre:
  - Programa com so aleatorio() tem import random, nao import math (FR-005, FR-006, FR-007)
  - Programa com so raiz(x) tem import math, nao import random (FR-005, FR-006, FR-010)
  - Programa com so absoluto(x) / minimo(a,b) nao tem import math nem random (FR-010)
  - Programa sem funcoes matematicas nao tem imports (SC-005)
  - Programa com raiz(x) + aleatorio() tem ambos os imports, cada um uma unica vez (FR-005, FR-010)
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


def _programa_com_multiplas_calls(calls):
    """Programa com funcao inicio que chama multiplas funcoes."""
    inicio = FunctionNode(
        nome="inicio",
        tipo_retorno=None,
        params=[],
        body=BlockNode(stmts=calls),
    )
    return ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")


class ImportSeletivosTest(unittest.TestCase):
    """Testes de imports seletivos para builtins matematicos (US2)."""

    def test_so_aleatorio_importa_random_nao_math(self):
        prog = _programa_com_call("aleatorio", [])
        py = emitir(prog)
        self.assertIn("import random", py)
        self.assertNotIn("import math", py)
        self.assertIn("random.random()", py)

    def test_so_raiz_importa_math_nao_random(self):
        prog = _programa_com_call("raiz", [LiteralNode(kind="int", value="4")])
        py = emitir(prog)
        self.assertIn("import math", py)
        self.assertNotIn("import random", py)
        self.assertIn("math.sqrt(4)", py)

    def test_so_absoluto_nao_importa_nada(self):
        prog = _programa_com_call("absoluto", [LiteralNode(kind="int", value="-5")])
        py = emitir(prog)
        self.assertNotIn("import math", py)
        self.assertNotIn("import random", py)
        self.assertIn("abs(-5)", py)

    def test_so_minimo_nao_importa_nada(self):
        prog = _programa_com_call(
            "minimo",
            [LiteralNode(kind="int", value="3"), LiteralNode(kind="int", value="7")],
        )
        py = emitir(prog)
        self.assertNotIn("import math", py)
        self.assertNotIn("import random", py)
        self.assertIn("min(3, 7)", py)

    def test_sem_funcoes_nao_importa_nada(self):
        inicio = FunctionNode(nome="inicio", body=BlockNode(stmts=[]))
        prog = ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertNotIn("import math", py)
        self.assertNotIn("import random", py)

    def test_raiz_e_aleatorio_importam_ambos(self):
        raiz_call = CallExprNode(
            callee=LiteralNode(kind="ident", value="raiz"),
            args=[LiteralNode(kind="int", value="4")],
        )
        aleatorio_call = CallExprNode(
            callee=LiteralNode(kind="ident", value="aleatorio"),
            args=[],
        )
        prog = _programa_com_multiplas_calls([raiz_call, aleatorio_call])
        py = emitir(prog)
        self.assertIn("import math", py)
        self.assertIn("import random", py)
        self.assertIn("math.sqrt(4)", py)
        self.assertIn("random.random()", py)
        self.assertEqual(py.count("import math"), 1)
        self.assertEqual(py.count("import random"), 1)


if __name__ == "__main__":
    unittest.main()
