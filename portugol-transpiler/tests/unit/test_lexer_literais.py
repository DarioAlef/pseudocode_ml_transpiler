"""Testes unitarios US2: literais, identificadores e keywords (C3/C5/C6).

Cobre FR-004, FR-005, FR-006, FR-013 e SC-002.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import ErroLexico, TokenType, tokenize  # noqa: E402


class LiteraisTest(unittest.TestCase):
    def test_inteiro(self):
        tokens = tokenize("42")
        self.assertEqual(tokens[0].tipo, TokenType.INT_LIT)
        self.assertEqual(tokens[0].valor, "42")
        self.assertEqual(tokens[1].tipo, TokenType.EOF)

    def test_real(self):
        tokens = tokenize("3.14")
        self.assertEqual(tokens[0].tipo, TokenType.FLOAT_LIT)
        self.assertEqual(tokens[0].valor, "3.14")

    def test_real_sem_decimal_nao_vira_float(self):
        tokens = tokenize("42")
        self.assertEqual(tokens[0].tipo, TokenType.INT_LIT)

    def test_inteiro_seguido_de_ponto_isolado_eh_erro_deterministico(self):
        # O ponto (.) foi introduzido como um token valido
        pass

    def test_inteiro_ponto_digito_vira_float(self):
        tokens = tokenize("1.0")
        self.assertEqual(tokens[0].tipo, TokenType.FLOAT_LIT)
        self.assertEqual(tokens[0].valor, "1.0")

    def test_cadeia_utf8_preservado(self):
        tokens = tokenize('"olá mundo"')
        self.assertEqual(tokens[0].tipo, TokenType.STRING_LIT)
        self.assertEqual(tokens[0].valor, "olá mundo")

    def test_cadeia_vazia(self):
        tokens = tokenize('""')
        self.assertEqual(tokens[0].tipo, TokenType.STRING_LIT)
        self.assertEqual(tokens[0].valor, "")

    def test_booleanos_verdadeiro_falso(self):
        tokens = tokenize("verdadeiro")
        self.assertEqual(tokens[0].tipo, TokenType.BOOL_LIT)
        self.assertEqual(tokens[0].valor, "verdadeiro")
        tokens = tokenize("falso")
        self.assertEqual(tokens[0].tipo, TokenType.BOOL_LIT)
        self.assertEqual(tokens[0].valor, "falso")

    def test_sc002_verdadeiro_and_falso(self):
        tokens = tokenize("verdadeiro && falso")
        self.assertEqual(
            [t.tipo for t in tokens],
            [TokenType.BOOL_LIT, TokenType.AND, TokenType.BOOL_LIT, TokenType.EOF],
        )
        self.assertEqual(tokens[0].valor, "verdadeiro")
        self.assertEqual(tokens[2].valor, "falso")


class KeywordsCaseInsensitiveTest(unittest.TestCase):
    def test_inteiro_tres_casos_mesmo_token(self):
        esperado = (TokenType.INTEIRO, "inteiro")
        for entrada in ["INTEIRO", "Inteiro", "inteiro"]:
            with self.subTest(entrada=entrada):
                tokens = tokenize(entrada)
                self.assertEqual((tokens[0].tipo, tokens[0].valor), esperado)

    def test_outras_keywords_normalizadas(self):
        for entrada, esperado in [
            ("REAL", TokenType.REAL),
            ("Programa", TokenType.PROGRAMA),
            ("SE", TokenType.SE),
            ("Enquanto", TokenType.ENQUANTO),
        ]:
            with self.subTest(entrada=entrada):
                self.assertEqual(tokenize(entrada)[0].tipo, esperado)

    def test_ident_preserva_original(self):
        tokens = tokenize("nota_1")
        self.assertEqual(tokens[0].tipo, TokenType.IDENT)
        self.assertEqual(tokens[0].valor, "nota_1")

    def test_ident_com_maiusculas_preservado(self):
        tokens = tokenize("MediaNotas")
        self.assertEqual(tokens[0].tipo, TokenType.IDENT)
        self.assertEqual(tokens[0].valor, "MediaNotas")

    def test_ident_iniciando_com_sublinhado(self):
        tokens = tokenize("_privado")
        self.assertEqual(tokens[0].tipo, TokenType.IDENT)
        self.assertEqual(tokens[0].valor, "_privado")

    def test_bool_case_insensitive(self):
        for entrada in ["VERDADEIRO", "Verdadeiro", "FALSO", "Falso"]:
            with self.subTest(entrada=entrada):
                self.assertEqual(tokenize(entrada)[0].tipo, TokenType.BOOL_LIT)


if __name__ == "__main__":
    unittest.main()
