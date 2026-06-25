"""Testes unitarios US2 (Card 11): emissao e valor de '^' -> '**'.

Cobre FR-008, SC-003: transpila e executa, conferindo os valores numericos
exatos das expressoes de potencia e sua precedencia.
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


def _executar(src):
    """Emite e executa o programa, devolvendo o stdout capturado."""
    codigo = emitir(parse(tokenize(src)))
    buffer = io.StringIO()
    ambiente = {"__name__": "__main__"}
    with redirect_stdout(buffer):
        exec(compile(codigo, "<gerado>", "exec"), ambiente)
    return buffer.getvalue()


_PROG = """programa {
  funcao inicio() {
    escreval(2 ^ 10)
    escreval(2 + 3 ^ 2)
    escreval(2 * 3 ^ 2)
    escreval(2 ^ 3 ^ 2)
  }
}"""


class PotenciaEmissaoTest(unittest.TestCase):
    def test_pot_emite_estrela_dupla(self):
        codigo = emitir(parse(tokenize(_PROG)))
        self.assertIn("**", codigo)
        self.assertNotIn("^", codigo)

    def test_valores_de_precedencia(self):
        linhas = _executar(_PROG).splitlines()
        self.assertEqual(linhas, ["1024", "11", "18", "512"])


if __name__ == "__main__":
    unittest.main()
