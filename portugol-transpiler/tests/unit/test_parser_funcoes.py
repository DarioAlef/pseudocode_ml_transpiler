"""Testes de funcoes com tipo de retorno e parametros (T020, US4, FR-003/FR-004).

Cobre: funcao com tipo de retorno, parametros escalares, parametro por
referencia (&) e parametro vetor/matriz.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from parser import Parser  # noqa: E402
from ast_nodes import FunctionNode, ParamNode, TypeNode  # noqa: E402


def _parse_funcao(decl_funcao):
    """Parseia um programa com a declaracao de funcao dada."""
    codigo = f"programa {{ {decl_funcao} }}"
    ast = Parser(tokenize(codigo)).parse()
    return ast.funcoes[0]


class FuncaoComRetornoTest(unittest.TestCase):
    def test_real_sigmoide(self):
        f = _parse_funcao("funcao real sigmoide(real z) { retorne z }")
        self.assertIsInstance(f, FunctionNode)
        self.assertEqual(f.nome, "sigmoide")
        self.assertIsNotNone(f.tipo_retorno)
        self.assertIsInstance(f.tipo_retorno, TypeNode)
        self.assertEqual(f.tipo_retorno.base, "real")

    def test_inteiro_com_retorno(self):
        f = _parse_funcao("funcao inteiro dobro(inteiro x) { retorne x }")
        self.assertEqual(f.tipo_retorno.base, "inteiro")
        self.assertEqual(f.nome, "dobro")

    def test_sem_retorno_e_none(self):
        f = _parse_funcao("funcao inicio() { }")
        self.assertIsNone(f.tipo_retorno)


class ParametrosTest(unittest.TestCase):
    def test_param_escalar(self):
        f = _parse_funcao("funcao real sigmoide(real z) { retorne z }")
        self.assertEqual(len(f.params), 1)
        p = f.params[0]
        self.assertIsInstance(p, ParamNode)
        self.assertEqual(p.nome, "z")
        self.assertEqual(p.tipo.base, "real")
        self.assertFalse(p.is_ref)

    def test_multiplos_params(self):
        f = _parse_funcao("funcao real f(real a, inteiro b) { retorne a }")
        self.assertEqual(len(f.params), 2)
        self.assertEqual(f.params[0].nome, "a")
        self.assertEqual(f.params[1].nome, "b")

    def test_param_por_referencia(self):
        f = _parse_funcao("funcao real f(&real v) { retorne v }")
        p = f.params[0]
        self.assertIsInstance(p, ParamNode)
        self.assertTrue(p.is_ref)
        self.assertEqual(p.tipo.base, "real")

    def test_param_vetor_por_ref(self):
        f = _parse_funcao("funcao real f(&real v[]) { retorne v }")
        p = f.params[0]
        self.assertTrue(p.is_ref)
        self.assertTrue(p.tipo.is_array)

    def test_sem_params(self):
        f = _parse_funcao("funcao inicio() { }")
        self.assertEqual(len(f.params), 0)


if __name__ == "__main__":
    unittest.main()
