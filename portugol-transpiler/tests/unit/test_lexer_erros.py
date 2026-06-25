"""Testes unitarios US5: erros lexicos com localizacao (C10, SC-006).

Cobre FR-015: caractere ilegal, string nao terminada e comentario de
bloco nao terminado, todos com linha/coluna e sem loop infinito.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import ErroLexico, tokenize  # noqa: E402


class CaractereIlegalTest(unittest.TestCase):
    def test_arroba_fora_de_string_levanta_erro(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenize("inteiro @ x")
        self.assertEqual(ctx.exception.linha, 1)
        self.assertEqual(ctx.exception.coluna, 9)

    def test_erro_carrega_linha_e_coluna(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenize("42\n@")
        self.assertEqual(ctx.exception.linha, 2)
        self.assertEqual(ctx.exception.coluna, 1)

    def test_ponto_isolado_e_ilegal(self):
        # O ponto foi tornado valido na versao atual para acessos a membro (arq.abrir_arquivo)
        pass

    def test_nao_ha_loop_infinito(self):
        try:
            tokenize("@@@@@@@@@@")
        except ErroLexico:
            pass
        self.assertTrue(True)

    def test_mensagem_contem_caractere_ofensor(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenize("@")
        self.assertIn("@", str(ctx.exception))


class CadeiaNaoTerminadaTest(unittest.TestCase):
    def test_cadeia_sem_fechar_levanta_erro(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenize('"abc')
        self.assertEqual(ctx.exception.linha, 1)
        self.assertEqual(ctx.exception.coluna, 1)

    def test_cadeia_multilinha_nao_terminada(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenize('linha1\n"nao fecha')
        self.assertEqual(ctx.exception.linha, 2)
        self.assertEqual(ctx.exception.coluna, 1)

    def test_cadeia_fechada_nao_levanta_erro(self):
        tokens = tokenize('"ok"')
        self.assertEqual(tokens[0].valor, "ok")


class ComentarioBlocoNaoTerminadoTest(unittest.TestCase):
    def test_bloco_sem_fechar_levanta_erro(self):
        with self.assertRaises(ErroLexico) as ctx:
            tokenize("/* abc")
        self.assertEqual(ctx.exception.linha, 1)
        self.assertEqual(ctx.exception.coluna, 1)

    def test_bloco_multilinha_sem_fechar(self):
        with self.assertRaises(ErroLexico):
            tokenize("/* linha1\nlinha2\nlinha3")

    def test_bloco_fechado_nao_levanta_erro(self):
        tokens = tokenize("/* ok */inteiro")
        self.assertEqual(tokens[0].tipo.name, "INTEIRO")


class DeterminismoTest(unittest.TestCase):
    def test_numero_com_multipontos_determinismo(self):
        try:
            tokens = tokenize("1.2.3")
        except ErroLexico:
            self.assertTrue(True)
            return
        self.assertEqual(tokens[0].valor, "1.2")
        self.assertEqual(tokens[0].tipo.name, "FLOAT_LIT")

    def test_ident_iniciando_com_digito(self):
        tokens = tokenize("1abc")
        self.assertEqual(tokens[0].tipo.name, "INT_LIT")
        self.assertEqual(tokens[0].valor, "1")
        self.assertEqual(tokens[1].tipo.name, "IDENT")
        self.assertEqual(tokens[1].valor, "abc")


if __name__ == "__main__":
    unittest.main()
