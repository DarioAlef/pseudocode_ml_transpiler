"""Testes de contrato US3 (Card 13): API publica de semantic_analyzer.

Cobre contracts/semantic_analyzer.md: assinatura de analisar, tipos expostos,
SymbolTable.tipo_de e ausencia de diagnosticos para programa valido.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from parser import parse  # noqa: E402
from semantic_analyzer import (  # noqa: E402
    Diagnostico,
    Scope,
    SemanticAnalyzer,
    Symbol,
    SymbolTable,
    analisar,
)

_VALIDO = """programa {
  real nota_1 = 0.0
  funcao real dobro(real v) {
    retorne v * 2.0
  }
  funcao inicio() {
    nota_1 = dobro(3.0)
    escreval(nota_1)
  }
}"""


def _analisar(src):
    return analisar(parse(tokenize(src)))


class ContratoAssinaturaTest(unittest.TestCase):
    def test_analisar_retorna_tupla(self):
        tabela, diags = _analisar(_VALIDO)
        self.assertIsInstance(tabela, SymbolTable)
        self.assertIsInstance(diags, list)

    def test_tipos_exportados_existem(self):
        self.assertTrue(callable(SemanticAnalyzer))
        self.assertTrue(callable(Scope))
        self.assertTrue(hasattr(Symbol, "__dataclass_fields__"))
        self.assertTrue(hasattr(Diagnostico, "__dataclass_fields__"))


class ContratoTipoDeTest(unittest.TestCase):
    def test_tipo_de_global(self):
        tabela, _ = _analisar(_VALIDO)
        self.assertEqual(tabela.tipo_de("nota_1"), "real")

    def test_tipo_de_desconhecido_none(self):
        tabela, _ = _analisar(_VALIDO)
        self.assertIsNone(tabela.tipo_de("inexistente"))


class ContratoProgramaValidoTest(unittest.TestCase):
    def test_programa_valido_sem_diagnosticos(self):
        _, diags = _analisar(_VALIDO)
        self.assertEqual(diags, [])


if __name__ == "__main__":
    unittest.main()
