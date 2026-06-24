"""Testes de erros sintaticos com linha/coluna (T015, US2, FR-018/FR-019/SC-003).

Cobre: delimitador nao fechado, fim prematuro de expressao, tokens sobrando
apos o programa e outros desvios gramaticais.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from parser import Parser, ErroSintatico  # noqa: E402


def _parse(codigo):
    return Parser(tokenize(codigo)).parse()


def _espera_erro(caso):
    """Retorna o ErroSintatico levantado ao parsear `caso`."""
    try:
        _parse(caso)
        raise AssertionError("deveria ter lancado ErroSintatico")
    except ErroSintatico as e:
        return e


class SC003ErroComPosicaoTest(unittest.TestCase):
    def _verifica_posicao(self, erro):
        self.assertIsInstance(erro.linha, int)
        self.assertIsInstance(erro.coluna, int)
        self.assertGreaterEqual(erro.linha, 1)
        self.assertGreaterEqual(erro.coluna, 1)

    def test_inicio_parentese_nao_fechado(self):
        e = _espera_erro("programa { funcao inicio( }")
        self._verifica_posicao(e)

    def test_brace_nao_fechado(self):
        e = _espera_erro("programa { funcao inicio() {")
        self._verifica_posicao(e)

    def test_expressao_incompleta(self):
        e = _espera_erro("programa { funcao inicio() { inteiro x = 1 + } }")
        self._verifica_posicao(e)

    def test_atribuicao_sem_valor(self):
        e = _espera_erro("programa { funcao inicio() { inteiro x x = } }")
        self._verifica_posicao(e)

    def test_mensagem_contem_esperado_e_encontrado(self):
        e = _espera_erro("programa { funcao inicio( }")
        texto = str(e).lower()
        self.assertIn("sintatico", texto)
        self.assertIn(str(e.linha), str(e))
        self.assertIn(str(e.coluna), str(e))


class FR019TokensSobrandoTest(unittest.TestCase):
    def test_token_extra_apos_programa(self):
        e = _espera_erro("programa { funcao inicio() { } } extra")
        self.assertIsInstance(e, ErroSintatico)
        self.assertIsInstance(e.linha, int)
        self.assertIsInstance(e.coluna, int)

    def test_dois_programas(self):
        e = _espera_erro(
            "programa { funcao inicio() { } } programa { funcao inicio() { } }"
        )
        self.assertIsInstance(e, ErroSintatico)


class MensagensTest(unittest.TestCase):
    def test_mensagem_nao_vazia(self):
        e = _espera_erro("programa { funcao inicio( }")
        self.assertGreater(len(e.mensagem), 0)

    def test_str_contem_linha_e_coluna(self):
        e = _espera_erro("programa { funcao inicio( }")
        s = str(e)
        self.assertIn(str(e.linha), s)
        self.assertIn(str(e.coluna), s)


if __name__ == "__main__":
    unittest.main()
