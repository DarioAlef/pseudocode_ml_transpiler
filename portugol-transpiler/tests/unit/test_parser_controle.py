"""Testes de controle de fluxo (T021, US4, FR-011/FR-012/FR-013/FR-014).

Cobre: se/senao se/senao, enquanto, para C-style, retorne.
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
    BlockNode,
    ForStmtNode,
    IfStmtNode,
    ReturnStmtNode,
    WhileStmtNode,
)


def _parse_stmts(corpo):
    codigo = f"programa {{ funcao inicio() {{ {corpo} }} }}"
    ast = Parser(tokenize(codigo)).parse()
    return ast.funcoes[0].body.stmts


class SeTest(unittest.TestCase):
    def test_se_simples(self):
        stmts = _parse_stmts("se (x) { }")
        self.assertIsInstance(stmts[0], IfStmtNode)

    def test_se_cond(self):
        stmts = _parse_stmts("se (x) { }")
        self.assertIsNotNone(stmts[0].cond)

    def test_se_then_e_bloco(self):
        stmts = _parse_stmts("se (x) { }")
        self.assertIsInstance(stmts[0].then, BlockNode)

    def test_se_sem_senao(self):
        stmts = _parse_stmts("se (x) { }")
        node = stmts[0]
        self.assertEqual(node.elifs, [])
        self.assertIsNone(node.else_)

    def test_se_senao(self):
        stmts = _parse_stmts("se (x) { } senao { }")
        node = stmts[0]
        self.assertIsInstance(node, IfStmtNode)
        self.assertIsNotNone(node.else_)
        self.assertIsInstance(node.else_, BlockNode)

    def test_se_senao_se(self):
        stmts = _parse_stmts("se (a) { } senao se (b) { } senao { }")
        node = stmts[0]
        self.assertEqual(len(node.elifs), 1)
        elif_cond, elif_body = node.elifs[0]
        self.assertIsNotNone(elif_cond)
        self.assertIsInstance(elif_body, BlockNode)
        self.assertIsNotNone(node.else_)


class EnquantoTest(unittest.TestCase):
    def test_enquanto_basico(self):
        stmts = _parse_stmts("enquanto (x) { }")
        self.assertIsInstance(stmts[0], WhileStmtNode)

    def test_enquanto_cond(self):
        stmts = _parse_stmts("enquanto (x) { }")
        self.assertIsNotNone(stmts[0].cond)

    def test_enquanto_body(self):
        stmts = _parse_stmts("enquanto (x) { }")
        self.assertIsInstance(stmts[0].body, BlockNode)


class ParaTest(unittest.TestCase):
    def test_para_com_incdec(self):
        stmts = _parse_stmts("para (inteiro i = 0; i < 10; i++) { }")
        self.assertIsInstance(stmts[0], ForStmtNode)

    def test_para_init(self):
        stmts = _parse_stmts("para (inteiro i = 0; i < 10; i++) { }")
        self.assertIsNotNone(stmts[0].init)

    def test_para_cond(self):
        stmts = _parse_stmts("para (inteiro i = 0; i < 10; i++) { }")
        self.assertIsNotNone(stmts[0].cond)

    def test_para_post(self):
        stmts = _parse_stmts("para (inteiro i = 0; i < 10; i++) { }")
        post = stmts[0].post
        self.assertIsInstance(post, AssignNode)

    def test_para_body(self):
        stmts = _parse_stmts("para (inteiro i = 0; i < 10; i++) { }")
        self.assertIsInstance(stmts[0].body, BlockNode)

    def test_para_dec(self):
        stmts = _parse_stmts("para (inteiro i = 10; i > 0; i--) { }")
        self.assertIsInstance(stmts[0], ForStmtNode)
        post = stmts[0].post
        self.assertIsInstance(post, AssignNode)


class RetorneTest(unittest.TestCase):
    def test_retorne_com_expr(self):
        stmts = _parse_stmts("retorne 42")
        self.assertIsInstance(stmts[0], ReturnStmtNode)
        self.assertIsNotNone(stmts[0].value)

    def test_retorne_sem_expr(self):
        stmts = _parse_stmts("retorne")
        self.assertIsInstance(stmts[0], ReturnStmtNode)
        self.assertIsNone(stmts[0].value)


if __name__ == "__main__":
    unittest.main()
