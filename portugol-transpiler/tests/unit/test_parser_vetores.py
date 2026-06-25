"""Testes de vetor/matriz: declaracao, acesso indexado, atribuicao (T022, US4).

Cobre FR-006 (decl vetor/matriz), FR-008 (atribuicao indexada), FR-016 (IndexExprNode 2D).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from parser import Parser  # noqa: E402
from ast_nodes import AssignNode, IndexExprNode, LiteralNode, TypeNode, VarDeclNode  # noqa: E402


def _parse_stmts(corpo):
    codigo = f"programa {{ funcao inicio() {{ {corpo} }} }}"
    ast = Parser(tokenize(codigo)).parse()
    return ast.funcoes[0].body.stmts


class DeclVetorTest(unittest.TestCase):
    def test_decl_vetor_1d(self):
        stmts = _parse_stmts("real v[10]")
        d = stmts[0]
        self.assertIsInstance(d, VarDeclNode)
        self.assertEqual(d.nome, "v")
        self.assertIsInstance(d.tipo, TypeNode)
        self.assertTrue(d.tipo.is_array)
        self.assertEqual(len(d.tipo.dims), 1)

    def test_decl_vetor_grande(self):
        stmts = _parse_stmts("real X[5000]")
        d = stmts[0]
        self.assertTrue(d.tipo.is_array)
        self.assertEqual(len(d.tipo.dims), 1)

    def test_decl_matriz_2d(self):
        stmts = _parse_stmts("real X[5000][4]")
        d = stmts[0]
        self.assertIsInstance(d, VarDeclNode)
        self.assertTrue(d.tipo.is_array)
        self.assertEqual(len(d.tipo.dims), 2)

    def test_tipo_base_preservado(self):
        stmts = _parse_stmts("inteiro v[5]")
        self.assertEqual(stmts[0].tipo.base, "inteiro")


class AcessoIndexadoTest(unittest.TestCase):
    def test_acesso_1d(self):
        stmts = _parse_stmts("real v[5] inteiro x = 0 real y y = v[x]")
        assign = stmts[3]
        self.assertIsInstance(assign, AssignNode)
        self.assertIsInstance(assign.valor, IndexExprNode)
        self.assertEqual(len(assign.valor.indices), 1)

    def test_acesso_2d(self):
        stmts = _parse_stmts("real m[3][3] inteiro i = 0 inteiro j = 0 real y y = m[i][j]")
        assign = stmts[4]
        self.assertIsInstance(assign, AssignNode)
        idx = assign.valor
        self.assertIsInstance(idx, IndexExprNode)
        self.assertEqual(len(idx.indices), 2)

    def test_base_e_ident(self):
        stmts = _parse_stmts("real v[5] inteiro i = 0 real y y = v[i]")
        assign = stmts[3]
        idx = assign.valor
        self.assertIsInstance(idx.base, LiteralNode)
        self.assertEqual(idx.base.kind, "ident")
        self.assertEqual(idx.base.value, "v")


class AtribuicaoIndexadaTest(unittest.TestCase):
    def test_atrib_indexada_1d(self):
        stmts = _parse_stmts("real v[5] inteiro i = 0 v[i] = 3")
        assign = stmts[2]
        self.assertIsInstance(assign, AssignNode)
        self.assertIsInstance(assign.alvo, IndexExprNode)

    def test_atrib_indexada_2d(self):
        stmts = _parse_stmts("real m[3][3] inteiro i = 0 inteiro j = 0 m[i][j] = 1")
        assign = stmts[3]
        self.assertIsInstance(assign, AssignNode)
        self.assertIsInstance(assign.alvo, IndexExprNode)
        self.assertEqual(len(assign.alvo.indices), 2)


if __name__ == "__main__":
    unittest.main()
