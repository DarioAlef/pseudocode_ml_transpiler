"""Testes de precedência e associatividade de expressões (T003, FR-009/FR-010).

Cobre: 2+3*4 (multiplicação antes da adição), 2^3^2 (potência direita-assoc),
parênteses, unário -/nao, precedência completa da cadeia.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from ast_nodes import (  # noqa: E402
    BinaryExprNode,
    LiteralNode,
    UnaryExprNode,
)


def _parse_expr(codigo):
    """Parseia um programa mínimo com uma atribuição e devolve o valor da expr."""
    from parser import Parser
    tokens = tokenize(f"programa {{ funcao inicio() {{ inteiro x = {codigo} }} }}")
    ast = Parser(tokens).parse()
    return ast.funcoes[0].body.stmts[0].init


class PrecedenciaAdicaoMultTest(unittest.TestCase):
    def test_2_mais_3_vezes_4(self):
        node = _parse_expr("2 + 3 * 4")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "+")
        self.assertIsInstance(node.left, LiteralNode)
        self.assertEqual(node.left.value, "2")
        self.assertIsInstance(node.right, BinaryExprNode)
        self.assertEqual(node.right.op, "*")

    def test_2_vezes_3_mais_4(self):
        node = _parse_expr("2 * 3 + 4")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "+")
        self.assertIsInstance(node.left, BinaryExprNode)
        self.assertEqual(node.left.op, "*")

    def test_soma_esq_assoc(self):
        node = _parse_expr("1 + 2 + 3")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "+")
        self.assertIsInstance(node.left, BinaryExprNode)
        self.assertEqual(node.left.op, "+")


class PotenciaTest(unittest.TestCase):
    def test_potencia_direita_assoc(self):
        node = _parse_expr("2 ^ 3 ^ 2")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "^")
        self.assertIsInstance(node.left, LiteralNode)
        self.assertEqual(node.left.value, "2")
        self.assertIsInstance(node.right, BinaryExprNode)
        self.assertEqual(node.right.op, "^")

    def test_mult_antes_pot(self):
        node = _parse_expr("2 ^ 3 * 4")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, BinaryExprNode)
        self.assertEqual(node.left.op, "^")


class ParentesesTest(unittest.TestCase):
    def test_parenteses_anulam_precedencia(self):
        node = _parse_expr("(2 + 3) * 4")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, BinaryExprNode)
        self.assertEqual(node.left.op, "+")

    def test_divisao_soma_parentetizada(self):
        node = _parse_expr("(nota_1 + nota_2) / 2")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "/")
        self.assertIsInstance(node.left, BinaryExprNode)
        self.assertEqual(node.left.op, "+")


class UnarioTest(unittest.TestCase):
    def test_menos_unario(self):
        node = _parse_expr("-5")
        self.assertIsInstance(node, UnaryExprNode)
        self.assertEqual(node.op, "-")
        self.assertIsInstance(node.operand, LiteralNode)

    def test_nao_unario(self):
        node = _parse_expr("nao verdadeiro")
        self.assertIsInstance(node, UnaryExprNode)

    def test_unario_antes_mult(self):
        node = _parse_expr("-2 * 3")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertEqual(node.op, "*")
        self.assertIsInstance(node.left, UnaryExprNode)


class LogicoTest(unittest.TestCase):
    def test_e_menos_prioritario_que_igualdade(self):
        node = _parse_expr("1 == 1 e 2 == 2")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertIn(node.op, ("e", "&&"))
        self.assertIsInstance(node.left, BinaryExprNode)
        self.assertEqual(node.left.op, "==")

    def test_ou_menos_prioritario_que_e(self):
        node = _parse_expr("verdadeiro e falso ou falso")
        self.assertIsInstance(node, BinaryExprNode)
        self.assertIn(node.op, ("ou", "||"))
        self.assertIsInstance(node.left, BinaryExprNode)


if __name__ == "__main__":
    unittest.main()
