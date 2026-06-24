"""Testes unitarios US3: operadores e pontuacao com desambigacao (C7/C8).

Cobre FR-007, FR-008, FR-009 (lookahead de 1, maior correspondencia).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import TokenType, tokenize  # noqa: E402


class DesambiguacaoOperadoresTest(unittest.TestCase):
    def _tipo_do_primeiro(self, entrada):
        return tokenize(entrada)[0].tipo

    def test_atribuicao_vs_igualdade(self):
        self.assertEqual(self._tipo_do_primeiro("="), TokenType.ASSIGN)
        self.assertEqual(self._tipo_do_primeiro("=="), TokenType.EQ)
        self.assertEqual(tokenize("a = b")[1].tipo, TokenType.ASSIGN)
        self.assertEqual(tokenize("a == b")[1].tipo, TokenType.EQ)

    def test_relacionais_2char(self):
        self.assertEqual(self._tipo_do_primeiro("<="), TokenType.LE)
        self.assertEqual(self._tipo_do_primeiro(">="), TokenType.GE)
        self.assertEqual(self._tipo_do_primeiro("!="), TokenType.NEQ)

    def test_relacionais_1char(self):
        self.assertEqual(self._tipo_do_primeiro("<"), TokenType.LT)
        self.assertEqual(self._tipo_do_primeiro(">"), TokenType.GT)

    def test_logicos_2char(self):
        self.assertEqual(self._tipo_do_primeiro("&&"), TokenType.AND)
        self.assertEqual(self._tipo_do_primeiro("||"), TokenType.OR)

    def test_logicos_texto(self):
        self.assertEqual(self._tipo_do_primeiro("e"), TokenType.AND)
        self.assertEqual(self._tipo_do_primeiro("ou"), TokenType.OR)
        self.assertEqual(self._tipo_do_primeiro("nao"), TokenType.NOT)
        self.assertEqual(self._tipo_do_primeiro("E"), TokenType.AND)
        self.assertEqual(self._tipo_do_primeiro("OU"), TokenType.OR)
        self.assertEqual(self._tipo_do_primeiro("Nao"), TokenType.NOT)

    def test_not_e_amp_isolados(self):
        self.assertEqual(self._tipo_do_primeiro("!"), TokenType.NOT)
        self.assertEqual(self._tipo_do_primeiro("&"), TokenType.AMP)

    def test_incremento_decremento(self):
        self.assertEqual(self._tipo_do_primeiro("++"), TokenType.INC)
        self.assertEqual(self._tipo_do_primeiro("--"), TokenType.DEC)

    def test_aritmeticos_1char(self):
        casos = {
            "+": TokenType.MAIS,
            "-": TokenType.MENOS,
            "*": TokenType.MULT,
            "/": TokenType.DIV,
            "%": TokenType.MOD,
            "^": TokenType.POT,
        }
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(self._tipo_do_primeiro(entrada), esperado)

    def test_sequencia_completa_operadores(self):
        tokens = tokenize("+ - * / % ^ = == != < > <= >= && || ! ++ -- &")
        esperado = [
            TokenType.MAIS,
            TokenType.MENOS,
            TokenType.MULT,
            TokenType.DIV,
            TokenType.MOD,
            TokenType.POT,
            TokenType.ASSIGN,
            TokenType.EQ,
            TokenType.NEQ,
            TokenType.LT,
            TokenType.GT,
            TokenType.LE,
            TokenType.GE,
            TokenType.AND,
            TokenType.OR,
            TokenType.NOT,
            TokenType.INC,
            TokenType.DEC,
            TokenType.AMP,
            TokenType.EOF,
        ]
        self.assertEqual([t.tipo for t in tokens], esperado)

    def test_maior_correspondencia_vence(self):
        self.assertEqual(self._tipo_do_primeiro(">=!"), TokenType.GE)
        self.assertEqual(tokenize(">=!")[1].tipo, TokenType.NOT)


class PontuacaoTest(unittest.TestCase):
    def test_todos_sinais_de_pontuacao(self):
        tokens = tokenize("( ) { } [ ] , ; :")
        esperado = [
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.LBRACE,
            TokenType.RBRACE,
            TokenType.LBRACKET,
            TokenType.RBRACKET,
            TokenType.VIRGULA,
            TokenType.PONTO_VIRGULA,
            TokenType.DOIS_PONTOS,
            TokenType.EOF,
        ]
        self.assertEqual([t.tipo for t in tokens], esperado)

    def test_valores_de_pontuacao(self):
        tokens = tokenize("( ) { } [ ] , ; :")
        valores = [t.valor for t in tokens if t.tipo != TokenType.EOF]
        self.assertEqual(valores, list("( ) { } [ ] , ; :".split()))


if __name__ == "__main__":
    unittest.main()
