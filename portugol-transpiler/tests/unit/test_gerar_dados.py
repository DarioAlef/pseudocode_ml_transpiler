"""Testes do gerador de dados sinteticos (US2, Card 15).

Valida reprodutibilidade (SC-003), formato do CSV (SC-004), a regra geradora
do rotulo (FR-003) e a preservacao do exemplos/dados.csv existente (FR-002).
"""

import csv
import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exemplos"))

from gerar_dados import gerar

_EXEMPLOS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exemplos")


def _hash_arquivo(caminho):
    """Devolve o sha256 do conteudo do arquivo em `caminho`."""
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class TestGerarDados(unittest.TestCase):
    """Suite do gerador exemplos/gerar_dados.py."""

    def test_reprodutibilidade_byte_a_byte(self):
        """SC-003: gerar duas vezes produz arquivos identicos."""
        with tempfile.TemporaryDirectory() as d:
            a = os.path.join(d, "a.csv")
            b = os.path.join(d, "b.csv")
            gerar(a)
            gerar(b)
            self.assertEqual(_hash_arquivo(a), _hash_arquivo(b))

    def test_cabecalho_e_contagem(self):
        """SC-004: 1 cabecalho + ~500 linhas (450-550), 5 campos por linha."""
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "dados.csv")
            gerar(caminho)
            with open(caminho, encoding="utf-8") as f:
                linhas = list(csv.reader(f))
        self.assertEqual(linhas[0], ["x1", "x2", "x3", "x4", "classe"])
        dados = linhas[1:]
        self.assertGreaterEqual(len(dados), 450)
        self.assertLessEqual(len(dados), 550)
        for linha in dados:
            self.assertEqual(len(linha), 5)

    def test_rotulo_binario_e_features_float(self):
        """SC-004/FR-002: 4 features float e rotulo em {0,1}."""
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "dados.csv")
            gerar(caminho)
            with open(caminho, encoding="utf-8") as f:
                linhas = list(csv.reader(f))[1:]
        for linha in linhas:
            for campo in linha[:4]:
                float(campo)
            self.assertIn(linha[4], ("0", "1"))

    def test_regra_geradora_do_rotulo(self):
        """FR-003: classe = 1 se 2*x1 - 1*x2 + 0.5*x3 - 0.3*x4 + 0.5 > 0."""
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "dados.csv")
            gerar(caminho)
            with open(caminho, encoding="utf-8") as f:
                linhas = list(csv.reader(f))[1:]
        for linha in linhas:
            x = [float(v) for v in linha[:4]]
            z = 2.0 * x[0] - 1.0 * x[1] + 0.5 * x[2] - 0.3 * x[3] + 0.5
            esperado = "1" if z > 0.0 else "0"
            self.assertEqual(linha[4], esperado)

    def test_preserva_dados_csv_existente(self):
        """FR-002: gerar em outro caminho nao altera exemplos/dados.csv."""
        dados_csv = os.path.join(_EXEMPLOS, "dados.csv")
        if not os.path.exists(dados_csv):
            self.skipTest("exemplos/dados.csv ausente")
        antes = _hash_arquivo(dados_csv)
        with tempfile.TemporaryDirectory() as d:
            gerar(os.path.join(d, "dados_sinteticos.csv"))
        self.assertEqual(antes, _hash_arquivo(dados_csv))


if __name__ == "__main__":
    unittest.main()
