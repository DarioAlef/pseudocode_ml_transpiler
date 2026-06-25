"""Testes unitarios US2 (Card 11): precedencia/associatividade de '^'.

Cobre FR-007, FR-009: '^' liga mais forte que '*' e e associativo a direita.
Inspeciona a forma da AST produzida pelo parser.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from ast_nodes import BinaryExprNode, LiteralNode  # noqa: E402
from lexer import tokenize  # noqa: E402
from parser import parse  # noqa: E402


def _expr_de(src_expr):
    """Parseia 'real r = <expr>' e devolve o no de inicializacao."""
    src = "programa { funcao inicio() { real r = " + src_expr + " } }"
    prog = parse(tokenize(src))
    var_decl = prog.funcoes[0].body.stmts[0]
    return var_decl.init


class AssociatividadeDireitaTest(unittest.TestCase):
    def test_2_pot_3_pot_2_associa_a_direita(self):
        no = _expr_de("2 ^ 3 ^ 2")
        self.assertIsInstance(no, BinaryExprNode)
        self.assertEqual(no.op, "^")
        self.assertIsInstance(no.left, LiteralNode)
        self.assertEqual(no.left.value, "2")
        self.assertIsInstance(no.right, BinaryExprNode)
        self.assertEqual(no.right.op, "^")
        self.assertEqual(no.right.left.value, "3")
        self.assertEqual(no.right.right.value, "2")


class PrecedenciaSobreMultiplicacaoTest(unittest.TestCase):
    def test_2_mult_3_pot_2_liga_pot_primeiro(self):
        no = _expr_de("2 * 3 ^ 2")
        self.assertIsInstance(no, BinaryExprNode)
        self.assertEqual(no.op, "*")
        self.assertEqual(no.left.value, "2")
        self.assertIsInstance(no.right, BinaryExprNode)
        self.assertEqual(no.right.op, "^")

    def test_2_mais_3_pot_2_liga_pot_primeiro(self):
        no = _expr_de("2 + 3 ^ 2")
        self.assertEqual(no.op, "+")
        self.assertIsInstance(no.right, BinaryExprNode)
        self.assertEqual(no.right.op, "^")


if __name__ == "__main__":
    unittest.main()
