"""Testes unitarios US4: comentarios e rastreio de posicao (C4/C9).

Cobre FR-010, FR-011, FR-012, SC-003 e SC-007.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import TokenType, tokenize  # noqa: E402


class ComentarioLinhaTest(unittest.TestCase):
    def test_sc003_comentario_linha_ignorado(self):
        tokens = tokenize("// comentario\ninteiro x")
        self.assertEqual(
            [t.tipo for t in tokens],
            [TokenType.INTEIRO, TokenType.IDENT, TokenType.EOF],
        )
        self.assertEqual(tokens[0].valor, "inteiro")
        self.assertEqual(tokens[1].valor, "x")

    def test_comentario_no_fim_sem_quebra(self):
        tokens = tokenize("inteiro x // nota")
        self.assertEqual(
            [t.tipo for t in tokens],
            [TokenType.INTEIRO, TokenType.IDENT, TokenType.EOF],
        )

    def test_comentario_contem_operadores_ignorados(self):
        tokens = tokenize("// a == b && c\n42")
        self.assertEqual(
            [t.tipo for t in tokens], [TokenType.INT_LIT, TokenType.EOF]
        )


class ComentarioBlocoTest(unittest.TestCase):
    def test_bloco_unica_linha_ignorado(self):
        tokens = tokenize("/* nota */inteiro")
        self.assertEqual(
            [t.tipo for t in tokens], [TokenType.INTEIRO, TokenType.EOF]
        )

    def test_bloco_multilinha_ignorado_conta_linhas(self):
        tokens = tokenize("/* linha1\nlinha2\nlinha3 */\nreal y")
        self.assertEqual(
            [t.tipo for t in tokens], [TokenType.REAL, TokenType.IDENT, TokenType.EOF]
        )
        self.assertEqual(tokens[0].linha, 4)
        self.assertEqual(tokens[0].coluna, 1)
        self.assertEqual(tokens[1].linha, 4)
        self.assertEqual(tokens[1].coluna, 6)

    def test_bloco_com_codigo_antes_e_depois(self):
        tokens = tokenize("inteiro /* x */ y")
        self.assertEqual(
            [t.tipo for t in tokens],
            [TokenType.INTEIRO, TokenType.IDENT, TokenType.EOF],
        )
        self.assertEqual(tokens[1].valor, "y")


class RastreioPosicaoTest(unittest.TestCase):
    def test_espacos_tabs_atualizam_coluna(self):
        tokens = tokenize("\t\t42")
        self.assertEqual(tokens[0].coluna, 3)

    def test_posicoes_em_entrada_multilinha(self):
        tokens = tokenize("a\nbb\nccc")
        self.assertEqual((tokens[0].linha, tokens[0].coluna), (1, 1))
        self.assertEqual((tokens[1].linha, tokens[1].coluna), (2, 1))
        self.assertEqual((tokens[2].linha, tokens[2].coluna), (3, 1))
        self.assertEqual(tokens[3].tipo, TokenType.EOF)

    def test_posicao_apos_comentario_linha(self):
        tokens = tokenize("// x\n  inteiro")
        self.assertEqual((tokens[0].linha, tokens[0].coluna), (2, 3))

    def test_coluna_correta_com_espacos_entre_tokens(self):
        tokens = tokenize("a    =    b")
        self.assertEqual((tokens[1].linha, tokens[1].coluna), (1, 6))
        self.assertEqual((tokens[2].linha, tokens[2].coluna), (1, 11))


if __name__ == "__main__":
    unittest.main()
