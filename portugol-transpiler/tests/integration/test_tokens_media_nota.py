"""Integracao US1: tokeniza 01_media_nota.por ponta-a-ponta (SC-004).

Valida que o arquivo-alvo e tokenizado sem erro, produz a sequencia
esperada de tipos (programa/funcao/inicio, decls real, escreva/leia como
IDENT, STRING_LIT, operadores/pontuacao) e termina em EOF.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import TokenType, tokenize  # noqa: E402

EXERCICIO = os.path.abspath(
    os.path.join(PROJECT_DIR, "..", "exercises_portugol", "01_media_nota.por")
)

TIPOS_ESPERADOS = [
    TokenType.PROGRAMA,
    TokenType.LBRACE,
    TokenType.FUNCAO,
    TokenType.INICIO,
    TokenType.LPAREN,
    TokenType.RPAREN,
    TokenType.LBRACE,
    TokenType.REAL,
    TokenType.IDENT,
    TokenType.REAL,
    TokenType.IDENT,
    TokenType.REAL,
    TokenType.IDENT,
    TokenType.IDENT,
    TokenType.LPAREN,
    TokenType.STRING_LIT,
    TokenType.RPAREN,
    TokenType.IDENT,
    TokenType.LPAREN,
    TokenType.IDENT,
    TokenType.RPAREN,
    TokenType.IDENT,
    TokenType.LPAREN,
    TokenType.STRING_LIT,
    TokenType.RPAREN,
    TokenType.IDENT,
    TokenType.LPAREN,
    TokenType.IDENT,
    TokenType.RPAREN,
    TokenType.IDENT,
    TokenType.ASSIGN,
    TokenType.LPAREN,
    TokenType.IDENT,
    TokenType.MAIS,
    TokenType.IDENT,
    TokenType.RPAREN,
    TokenType.DIV,
    TokenType.INT_LIT,
    TokenType.IDENT,
    TokenType.LPAREN,
    TokenType.STRING_LIT,
    TokenType.VIRGULA,
    TokenType.IDENT,
    TokenType.RPAREN,
    TokenType.RBRACE,
    TokenType.RBRACE,
    TokenType.EOF,
]


class TokensMediaNotaTest(unittest.TestCase):
    def setUp(self):
        with open(EXERCICIO, encoding="utf-8") as f:
            self.conteudo = f.read()

    def test_arquivo_existe(self):
        self.assertTrue(os.path.isfile(EXERCICIO))

    def test_tokeniza_sem_erro_e_termina_em_eof(self):
        tokens = tokenize(self.conteudo)
        self.assertEqual(tokens[-1].tipo, TokenType.EOF)

    def test_sequencia_de_tipos_correspondente(self):
        tokens = tokenize(self.conteudo)
        self.assertEqual([t.tipo for t in tokens], TIPOS_ESPERADOS)

    def test_escreva_e_leia_sao_ident(self):
        tokens = tokenize(self.conteudo)
        valores = [t.valor for t in tokens if t.tipo == TokenType.IDENT]
        self.assertIn("escreva", valores)
        self.assertIn("leia", valores)
        self.assertIn("nota_1", valores)
        self.assertIn("nota_2", valores)
        self.assertIn("media", valores)

    def test_string_lit_preserva_conteudo_utf8(self):
        tokens = tokenize(self.conteudo)
        strings = [t.valor for t in tokens if t.tipo == TokenType.STRING_LIT]
        self.assertIn("A média da nota do aluno é: ", strings)
        self.assertIn("Digite a primeira nota:", strings)


if __name__ == "__main__":
    unittest.main()
