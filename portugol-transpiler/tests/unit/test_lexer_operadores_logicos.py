"""Testes unitarios US1 (Card 10): operadores logicos por extenso.

Cobre FR-001 (e/ou/nao viram AND/OR/NOT) e FR-003 (identificadores que
contem essas sequencias como prefixo/sufixo/substring permanecem IDENT).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import TokenType, tokenize  # noqa: E402


class PalavrasLogicasTest(unittest.TestCase):
    """Valida que e/ou/nao isolados sao operadores logicos."""

    def _primeiro(self, entrada):
        return tokenize(entrada)[0].tipo

    def test_e_vira_and(self):
        self.assertEqual(self._primeiro("e"), TokenType.AND)

    def test_ou_vira_or(self):
        self.assertEqual(self._primeiro("ou"), TokenType.OR)

    def test_nao_vira_not(self):
        self.assertEqual(self._primeiro("nao"), TokenType.NOT)

    def test_expressao_x_e_y(self):
        tokens = tokenize("x e y")
        self.assertEqual(
            [t.tipo for t in tokens[:3]],
            [TokenType.IDENT, TokenType.AND, TokenType.IDENT],
        )


class IdentificadoresIntegrosTest(unittest.TestCase):
    """Valida FR-003: nao fragmentar identificadores que contem e/ou/nao."""

    def _tipo_unico_ident(self, nome):
        tokens = tokenize(nome)
        self.assertEqual(tokens[0].tipo, TokenType.IDENT)
        self.assertEqual(tokens[0].valor, nome)
        self.assertEqual(tokens[1].tipo, TokenType.EOF)

    def test_erro_permanece_ident(self):
        self._tipo_unico_ident("erro")

    def test_numero_permanece_ident(self):
        self._tipo_unico_ident("numero")

    def test_outro_permanece_ident(self):
        self._tipo_unico_ident("outro")

    def test_naoSei_permanece_ident(self):
        self._tipo_unico_ident("naoSei")


if __name__ == "__main__":
    unittest.main()
