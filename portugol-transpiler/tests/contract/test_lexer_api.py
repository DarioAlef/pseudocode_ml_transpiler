"""Contrato da API do lexer (US1, espelha contracts/lexer-api.md).

Cobre C1 (termina em EOF / entrada vazia), C2 (declaracao com atribuicao,
SC-001) e C9 (rastreio de linha/coluna, SC-007).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import TokenType, tokenize  # noqa: E402


def _tipos(tokens):
    return [t.tipo for t in tokens]


class C1EofTerminacaoTest(unittest.TestCase):
    def test_entrada_vazia_devolve_apenas_eof(self):
        tokens = tokenize("")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].tipo, TokenType.EOF)
        self.assertEqual(tokens[0].valor, "")
        self.assertEqual(tokens[0].linha, 1)
        self.assertEqual(tokens[0].coluna, 1)

    def test_ultima_posicao_sempre_eof(self):
        for entrada in ["42", "inteiro x", "a == b && c", "verdadeiro\nfalso"]:
            with self.subTest(entrada=entrada):
                self.assertEqual(tokenize(entrada)[-1].tipo, TokenType.EOF)


class C2DeclaracaoComAtribuicaoTest(unittest.TestCase):
    def test_inteiro_x_igual_42(self):
        tokens = tokenize("inteiro x = 42")
        self.assertEqual(
            _tipos(tokens),
            [
                TokenType.INTEIRO,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.INT_LIT,
                TokenType.EOF,
            ],
        )
        self.assertEqual(tokens[0].valor, "inteiro")
        self.assertEqual(tokens[1].valor, "x")
        self.assertEqual(tokens[2].valor, "=")
        self.assertEqual(tokens[3].valor, "42")
        self.assertEqual(tokens[4].valor, "")


class C9PosicaoTest(unittest.TestCase):
    def test_posicoes_unica_linha(self):
        tokens = tokenize("inteiro x = 42")
        self.assertEqual((tokens[0].linha, tokens[0].coluna), (1, 1))
        self.assertEqual((tokens[1].linha, tokens[1].coluna), (1, 9))
        self.assertEqual((tokens[2].linha, tokens[2].coluna), (1, 11))
        self.assertEqual((tokens[3].linha, tokens[3].coluna), (1, 13))
        self.assertEqual((tokens[4].linha, tokens[4].coluna), (1, 15))

    def test_posicao_multilinha_reinicia_coluna(self):
        tokens = tokenize("inteiro x\nreal y")
        self.assertEqual((tokens[0].linha, tokens[0].coluna), (1, 1))
        self.assertEqual((tokens[1].linha, tokens[1].coluna), (1, 9))
        self.assertEqual((tokens[2].linha, tokens[2].coluna), (2, 1))
        self.assertEqual((tokens[3].linha, tokens[3].coluna), (2, 6))
        self.assertEqual(tokens[4].tipo, TokenType.EOF)

    def test_token_carrega_inicio_do_lexema(self):
        tokens = tokenize("   42")
        self.assertEqual((tokens[0].linha, tokens[0].coluna), (1, 4))


if __name__ == "__main__":
    unittest.main()
