"""Testes unitarios US3 (Card 13): diagnosticos da analise semantica.

Cobre FR-013 (variavel nao declarada -> aviso com linha), FR-014 (aridade ->
erro nao-fatal), FR-015 (retorno em procedimento -> aviso), alem de shadowing
e isencao de builtins (research.md D6/D7).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from parser import parse  # noqa: E402
from semantic_analyzer import analisar  # noqa: E402


def _diags(src):
    _, diagnosticos = analisar(parse(tokenize(src)))
    return diagnosticos


def _por_severidade(diagnosticos, severidade):
    return [d for d in diagnosticos if d.severidade == severidade]


class VariavelNaoDeclaradaTest(unittest.TestCase):
    def test_uso_sem_declaracao_gera_aviso_com_linha(self):
        src = (
            "programa {\n"
            "  funcao inicio() {\n"
            "    real x\n"
            "    x = y + 1\n"
            "  }\n"
            "}"
        )
        diagnosticos = _diags(src)
        avisos = _por_severidade(diagnosticos, "aviso")
        self.assertEqual(len(avisos), 1)
        self.assertIn("y", avisos[0].mensagem)
        self.assertEqual(avisos[0].linha, 4)


class AridadeTest(unittest.TestCase):
    def test_aridade_errada_gera_erro(self):
        src = (
            "programa {\n"
            "  funcao real soma(real a, real b) {\n"
            "    retorne a + b\n"
            "  }\n"
            "  funcao inicio() {\n"
            "    escreval(soma(1.0))\n"
            "  }\n"
            "}"
        )
        erros = _por_severidade(_diags(src), "erro")
        self.assertEqual(len(erros), 1)
        self.assertIn("soma", erros[0].mensagem)

    def test_aridade_correta_sem_erro(self):
        src = (
            "programa {\n"
            "  funcao real soma(real a, real b) {\n"
            "    retorne a + b\n"
            "  }\n"
            "  funcao inicio() {\n"
            "    escreval(soma(1.0, 2.0))\n"
            "  }\n"
            "}"
        )
        self.assertEqual(_por_severidade(_diags(src), "erro"), [])


class RetornoEmProcedimentoTest(unittest.TestCase):
    def test_retorno_com_valor_em_procedimento_gera_aviso(self):
        src = (
            "programa {\n"
            "  funcao p() {\n"
            "    retorne 1\n"
            "  }\n"
            "  funcao inicio() {\n"
            "  }\n"
            "}"
        )
        avisos = _por_severidade(_diags(src), "aviso")
        self.assertEqual(len(avisos), 1)


class ShadowingTest(unittest.TestCase):
    def test_param_sombreia_global_sem_aviso(self):
        src = (
            "programa {\n"
            "  inteiro contador = 0\n"
            "  funcao f(inteiro contador) {\n"
            "    contador = contador + 1\n"
            "  }\n"
            "  funcao inicio() {\n"
            "  }\n"
            "}"
        )
        self.assertEqual(_por_severidade(_diags(src), "aviso"), [])


class BuiltinsIsentosTest(unittest.TestCase):
    def test_builtins_nao_geram_diagnostico(self):
        src = (
            "programa {\n"
            "  funcao inicio() {\n"
            "    escreval(raiz(4.0))\n"
            "  }\n"
            "}"
        )
        self.assertEqual(_diags(src), [])


if __name__ == "__main__":
    unittest.main()
