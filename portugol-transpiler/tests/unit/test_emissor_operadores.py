"""Testes unitarios US1 (Card 10): emissor normaliza operadores logicos.

Cobre FR-004, FR-005, FR-009: e/&& -> and, ou/|| -> or, nao/! -> not, com
precedencia nao > e > ou. Verifica equivalencia palavra <-> simbolo.
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from emissor import emitir  # noqa: E402
from lexer import tokenize  # noqa: E402
from parser import parse  # noqa: E402


def _emitir(src):
    """Tokeniza, parseia e emite o codigo Python de um programa-fonte."""
    return emitir(parse(tokenize(src)))


def _executar(src):
    """Emite e executa o programa, devolvendo o stdout capturado."""
    codigo = _emitir(src)
    buffer = io.StringIO()
    ambiente = {"__name__": "__main__"}
    with redirect_stdout(buffer):
        exec(compile(codigo, "<gerado>", "exec"), ambiente)
    return buffer.getvalue()


_COND = """programa {{
  funcao inicio() {{
    inteiro x = 1
    inteiro y = 1
    logico ok = verdadeiro
    se ({cond}) {{ escreval("SIM") }}
  }}
}}"""


class NormalizacaoOperadoresTest(unittest.TestCase):
    """Mapeamento palavra/simbolo -> and/or/not no codigo gerado."""

    def test_e_gera_and(self):
        self.assertIn("and", _emitir(_COND.format(cond="x > 0 e y > 0")))

    def test_amp_amp_gera_and(self):
        self.assertIn("and", _emitir(_COND.format(cond="x > 0 && y > 0")))

    def test_ou_gera_or(self):
        self.assertIn("or", _emitir(_COND.format(cond="x > 0 ou y > 0")))

    def test_pipe_gera_or(self):
        self.assertIn("or", _emitir(_COND.format(cond="x > 0 || y > 0")))

    def test_nao_gera_not(self):
        self.assertIn("not", _emitir(_COND.format(cond="nao ok")))

    def test_bang_gera_not(self):
        self.assertIn("not", _emitir(_COND.format(cond="!ok")))


class EquivalenciaPalavraSimboloTest(unittest.TestCase):
    """Palavra e simbolo produzem o mesmo resultado de execucao (SC-002)."""

    def test_e_equivale_amp(self):
        self.assertEqual(
            _executar(_COND.format(cond="x > 0 e y > 0")),
            _executar(_COND.format(cond="x > 0 && y > 0")),
        )

    def test_nao_equivale_bang(self):
        self.assertEqual(
            _executar(_COND.format(cond="nao ok")),
            _executar(_COND.format(cond="!ok")),
        )


class PrecedenciaLogicaTest(unittest.TestCase):
    """nao > e > ou: 'verdadeiro ou verdadeiro e falso' = verdadeiro."""

    def test_e_liga_antes_de_ou(self):
        src = _COND.format(cond="verdadeiro ou verdadeiro e falso")
        self.assertEqual(_executar(src), "SIM\n")

    def test_nao_liga_antes_de_e(self):
        src = _COND.format(cond="nao falso e verdadeiro")
        self.assertEqual(_executar(src), "SIM\n")


if __name__ == "__main__":
    unittest.main()
