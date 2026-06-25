"""Testes unitarios de statements basicos (T009, US1, FR-005/FR-007/FR-008/FR-015/FR-017).

Cobre: declaracao escalar sem init, atribuicao IDENT = expr,
comando de chamada (escreva/leia -> CallExprNode).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from parser import Parser  # noqa: E402
from ast_nodes import (  # noqa: E402
    AssignNode,
    CallExprNode,
    LiteralNode,
    TypeNode,
    VarDeclNode,
)


def _parse_stmts(corpo):
    """Parseia corpo de funcao e retorna lista de statements."""
    codigo = f"programa {{ funcao inicio() {{ {corpo} }} }}"
    ast = Parser(tokenize(codigo)).parse()
    return ast.funcoes[0].body.stmts


class VarDeclEscalarTest(unittest.TestCase):
    def test_decl_real_sem_init(self):
        stmts = _parse_stmts("real media")
        self.assertEqual(len(stmts), 1)
        d = stmts[0]
        self.assertIsInstance(d, VarDeclNode)
        self.assertEqual(d.nome, "media")
        self.assertIsInstance(d.tipo, TypeNode)
        self.assertEqual(d.tipo.base, "real")
        self.assertIsNone(d.init)

    def test_decl_inteiro_sem_init(self):
        stmts = _parse_stmts("inteiro n")
        d = stmts[0]
        self.assertIsInstance(d, VarDeclNode)
        self.assertEqual(d.tipo.base, "inteiro")
        self.assertIsNone(d.init)

    def test_decl_logico_sem_init(self):
        stmts = _parse_stmts("logico ok")
        d = stmts[0]
        self.assertEqual(d.tipo.base, "logico")

    def test_decl_cadeia_sem_init(self):
        stmts = _parse_stmts('cadeia nome')
        d = stmts[0]
        self.assertEqual(d.tipo.base, "cadeia")

    def test_decl_com_init(self):
        stmts = _parse_stmts("inteiro x = 42")
        d = stmts[0]
        self.assertIsInstance(d, VarDeclNode)
        self.assertIsNotNone(d.init)
        self.assertIsInstance(d.init, LiteralNode)
        self.assertEqual(d.init.value, "42")


class AtribuicaoTest(unittest.TestCase):
    def test_atribuicao_simples(self):
        stmts = _parse_stmts("real x x = 5")
        assign = stmts[1]
        self.assertIsInstance(assign, AssignNode)
        self.assertEqual(assign.op, "=")
        alvo = assign.alvo
        self.assertIsInstance(alvo, LiteralNode)
        self.assertEqual(alvo.kind, "ident")
        self.assertEqual(alvo.value, "x")

    def test_atribuicao_expr(self):
        stmts = _parse_stmts("real x real y x = y + 1")
        assign = stmts[2]
        self.assertIsInstance(assign, AssignNode)
        from ast_nodes import BinaryExprNode
        self.assertIsInstance(assign.valor, BinaryExprNode)


class ChamadaTest(unittest.TestCase):
    def test_escreva_com_string(self):
        stmts = _parse_stmts('escreva("ola")')
        c = stmts[0]
        self.assertIsInstance(c, CallExprNode)
        self.assertIsInstance(c.callee, LiteralNode)
        self.assertEqual(c.callee.value, "escreva")
        self.assertEqual(len(c.args), 1)
        self.assertIsInstance(c.args[0], LiteralNode)
        self.assertEqual(c.args[0].kind, "cadeia")

    def test_leia_com_variavel(self):
        stmts = _parse_stmts("real x leia(x)")
        c = stmts[1]
        self.assertIsInstance(c, CallExprNode)
        self.assertEqual(c.callee.value, "leia")
        self.assertEqual(len(c.args), 1)

    def test_escreva_multiplos_args(self):
        stmts = _parse_stmts('escreva("res:", x)')
        c = stmts[0]
        self.assertIsInstance(c, CallExprNode)
        self.assertEqual(len(c.args), 2)

    def test_chamada_sem_args(self):
        stmts = _parse_stmts("foo()")
        c = stmts[0]
        self.assertIsInstance(c, CallExprNode)
        self.assertEqual(len(c.args), 0)


if __name__ == "__main__":
    unittest.main()
