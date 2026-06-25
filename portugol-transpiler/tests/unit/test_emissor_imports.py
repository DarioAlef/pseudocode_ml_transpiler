"""Testes unitarios de imports seletivos do emissor (T027, US3).

Cobre: programa sem ler_csv NAO contem `from runtime_portugol import ler_csv`
(FR-003); programa com exp/logaritmo contem `import math` (FR-002); programa
com aleatorio() contem `import random`; 1a linha sempre o cabecalho (FR-001).
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

CABECALHO = "# GERADO AUTOMATICAMENTE — NÃO EDITE"


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


class CabecalhoTest(unittest.TestCase):
    def test_primeira_linha_sempre_cabecalho(self):
        prog = _programa_com_call("escreva", [LiteralNode(kind="cadeia", value="oi")])
        py = emitir(prog)
        self.assertEqual(py.splitlines()[0], CABECALHO)

    def test_programa_vazio_sem_imports(self):
        inicio = FunctionNode(nome="inicio", body=BlockNode(stmts=[]))
        prog = ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertNotIn("import math", py)
        self.assertNotIn("import random", py)
        self.assertNotIn("from runtime_portugol", py)


class ImportMathTest(unittest.TestCase):
    def test_exp_dispara_import_math(self):
        prog = _programa_com_call(
            "exp",
            [LiteralNode(kind="real", value="1.0")],
        )
        py = emitir(prog)
        self.assertIn("import math", py)
        self.assertIn("math.exp", py)

    def test_logaritmo_dispara_import_math(self):
        prog = _programa_com_call(
            "logaritmo",
            [LiteralNode(kind="int", value="1")],
        )
        py = emitir(prog)
        self.assertIn("import math", py)
        self.assertIn("math.log", py)

    def test_raiz_dispara_import_math(self):
        prog = _programa_com_call("raiz", [LiteralNode(kind="int", value="4")])
        py = emitir(prog)
        self.assertIn("import math", py)
        self.assertIn("math.sqrt", py)

    def test_potencia_dispara_import_math(self):
        prog = _programa_com_call(
            "potencia",
            [LiteralNode(kind="int", value="2"), LiteralNode(kind="int", value="3")],
        )
        py = emitir(prog)
        self.assertIn("import math", py)
        self.assertIn("math.pow", py)

    def test_sem_math_nao_importa_math(self):
        prog = _programa_com_call("escreva", [LiteralNode(kind="cadeia", value="oi")])
        py = emitir(prog)
        self.assertNotIn("import math", py)


class ImportRandomTest(unittest.TestCase):
    def test_aleatorio_dispara_import_random(self):
        prog = _programa_com_call("aleatorio", [])
        py = emitir(prog)
        self.assertIn("import random", py)
        self.assertIn("random.random", py)

    def test_sem_aleatorio_nao_importa_random(self):
        prog = _programa_com_call("escreva", [LiteralNode(kind="cadeia", value="oi")])
        py = emitir(prog)
        self.assertNotIn("import random", py)


class ImportRuntimeTest(unittest.TestCase):
    def test_ler_csv_dispara_import_runtime(self):
        prog = _programa_com_call(
            "ler_csv",
            [LiteralNode(kind="cadeia", value="dados.csv")],
        )
        py = emitir(prog)
        self.assertIn("from runtime_portugol import ler_csv", py)
        self.assertIn("ler_csv(\"dados.csv\")", py)

    def test_normalizar_zscore_dispara_import_runtime(self):
        prog = _programa_com_call(
            "normalizar_zscore",
            [LiteralNode(kind="ident", value="X")],
        )
        py = emitir(prog)
        self.assertIn("from runtime_portugol import", py)
        self.assertIn("normalizar_zscore", py)

    def test_sem_runtime_nao_importa_runtime(self):
        prog = _programa_com_call("escreva", [LiteralNode(kind="cadeia", value="oi")])
        py = emitir(prog)
        self.assertNotIn("from runtime_portugol", py)


if __name__ == "__main__":
    unittest.main()
