"""Testes unitarios US4 (Card 12): leia(x) com conversao de tipo.

Cobre FR-018, FR-019, FR-020, FR-021: conversao por tipo declarado
(inteiro/real/cadeia/logico), fallback float, e leia com multiplas variaveis.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from emissor import emitir  # noqa: E402
from lexer import tokenize  # noqa: E402
from parser import parse  # noqa: E402

_LOGICO_RHS = 'input().strip().lower() in ("verdadeiro", "true", "1")'


def _emitir(decls_e_leia):
    """Monta inicio com o corpo informado e devolve o codigo gerado."""
    src = "programa { funcao inicio() {\n" + decls_e_leia + "\n} }"
    return emitir(parse(tokenize(src)))


class LeiaPorTipoTest(unittest.TestCase):
    def test_inteiro_usa_int(self):
        py = _emitir("inteiro idade\nleia(idade)")
        self.assertIn("idade = int(input())", py)

    def test_real_usa_float(self):
        py = _emitir("real nota_1\nleia(nota_1)")
        self.assertIn("nota_1 = float(input())", py)

    def test_cadeia_sem_conversao(self):
        py = _emitir("cadeia nome\nleia(nome)")
        self.assertIn("nome = input()", py)
        self.assertNotIn("nome = float(input())", py)

    def test_logico_leitura_booleana(self):
        py = _emitir("logico ativo\nleia(ativo)")
        self.assertIn(f"ativo = {_LOGICO_RHS}", py)

    def test_tipo_desconhecido_usa_float(self):
        py = _emitir("leia(x)")
        self.assertIn("x = float(input())", py)


class LeiaMultiplasVariaveisTest(unittest.TestCase):
    def test_duas_variaveis_uma_linha_cada(self):
        py = _emitir("inteiro a\nreal b\nleia(a, b)")
        self.assertIn("a = int(input())", py)
        self.assertIn("b = float(input())", py)

    def test_ordem_preservada(self):
        py = _emitir("inteiro a\nreal b\nleia(a, b)")
        self.assertLess(py.index("a = int(input())"), py.index("b = float(input())"))

    def test_logico_e_cadeia_juntos(self):
        py = _emitir("cadeia nome\nlogico ativo\nleia(nome, ativo)")
        self.assertIn("nome = input()", py)
        self.assertIn(f"ativo = {_LOGICO_RHS}", py)


if __name__ == "__main__":
    unittest.main()
