"""Teste de integracao da meta final: regressao_logistica.por (T028, US3, SC-005).

Valida que o .por de exemplo transpila e o .py gerado passa em py_compile,
roda o treinamento da regressao logistica (treino/teste separados) e valida a
acuracia final >= 0.95 medida sobre o conjunto de TESTE (held-out).
"""

import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "exemplos"))

from gerar_dados import gerar

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAMINHO_REG = os.path.join(PROJECT_DIR, "exemplos", "regressao_logistica.por")
SAIDA_PY = os.path.join(PROJECT_DIR, "portugol_out", "regressao_logistica.py")


def _run_cli(*args):
    """Executa a CLI transpilador.py com argumentos."""
    return subprocess.run(
        [sys.executable, "transpilador.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )


class SC005RegressaoCompilaTest(unittest.TestCase):
    """Suite de testes integrados para validacao da regressao logistica."""

    def setUp(self):
        """Prepara o ambiente limpando os arquivos gerados."""
        self._portugol_out = os.path.join(PROJECT_DIR, "portugol_out")
        self._caminho_csv = os.path.join(self._portugol_out, "dados_sinteticos.csv")
        self._caminho_modelo = os.path.join(self._portugol_out, "modelo.txt")
        self._remover_arquivos()

    def tearDown(self):
        """Limpa o ambiente apos a execucao."""
        self._remover_arquivos()

    def _remover_arquivos(self):
        """Remove os arquivos de teste temporarios se existirem."""
        for arq in [SAIDA_PY, self._caminho_csv, self._caminho_modelo]:
            if os.path.exists(arq):
                os.unlink(arq)

    def test_transpila_sem_erro(self):
        """Valida que o transpilador executa sem erros."""
        r = _run_cli(CAMINHO_REG)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_py_gerado_existe(self):
        """Valida que o arquivo Python foi criado no local correto."""
        _run_cli(CAMINHO_REG)
        self.assertTrue(os.path.exists(SAIDA_PY))

    def test_py_compile_retorna_zero(self):
        """Valida que o arquivo Python gerado e sintaticamente valido."""
        _run_cli(CAMINHO_REG)
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", SAIDA_PY],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_primeira_linha_e_cabecalho(self):
        """Valida que a primeira linha contem a string de cabecalho."""
        _run_cli(CAMINHO_REG)
        with open(SAIDA_PY, encoding="utf-8") as f:
            primeira = f.readline().rstrip("\n")
        self.assertEqual(primeira, "# GERADO AUTOMATICAMENTE — NÃO EDITE")

    def test_sem_tabs_no_gerado(self):
        """Valida a ausencia de tabs no arquivo gerado."""
        _run_cli(CAMINHO_REG)
        with open(SAIDA_PY, encoding="utf-8") as f:
            conteudo = f.read()
        self.assertNotIn("\t", conteudo)

    def test_imports_seletivos_runtime_e_math(self):
        """Valida que os modulo math e runtime_portugol sao importados."""
        _run_cli(CAMINHO_REG)
        with open(SAIDA_PY, encoding="utf-8") as f:
            conteudo = f.read()
        self.assertIn("from runtime_portugol import", conteudo)
        self.assertIn("import math", conteudo)

    def test_regressao_executa_e_treina(self):
        """Gera dataset sintetico (via gerar_dados), treina e valida acuracia >= 0.95."""
        os.makedirs(self._portugol_out, exist_ok=True)
        gerar(self._caminho_csv)

        r = _run_cli(CAMINHO_REG, "--run")
        self.assertEqual(r.returncode, 0, r.stderr)

        self.assertIn("Treino:", r.stdout)
        self.assertIn("Teste:", r.stdout)

        self.assertIn("Acuracia final", r.stdout)
        accuracy_line = [
            line for line in r.stdout.splitlines() if "Acuracia final" in line
        ]
        self.assertTrue(len(accuracy_line) > 0)
        accuracy_val = float(accuracy_line[0].split(":")[1].strip())
        self.assertGreaterEqual(accuracy_val, 0.95)

        self.assertTrue(os.path.exists(self._caminho_modelo))
        with open(self._caminho_modelo, encoding="utf-8") as f:
            linhas = f.readlines()
        self.assertEqual(len(linhas), 2)
        pesos_gerados = [float(p) for p in linhas[0].split()]
        bias_gerado = float(linhas[1].strip())
        self.assertEqual(len(pesos_gerados), 4)
        self.assertIsNotNone(bias_gerado)

    def _treinar_e_capturar_stdout(self):
        """Gera dados, roda --run e devolve o stdout do treino (helper)."""
        os.makedirs(self._portugol_out, exist_ok=True)
        gerar(self._caminho_csv)
        r = _run_cli(CAMINHO_REG, "--run")
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_custo_diminui_ao_longo_das_epocas(self):
        """SC-002: o custo final reportado e estritamente menor que o inicial."""
        stdout = self._treinar_e_capturar_stdout()
        custos = [
            float(line.split("custo:")[1].strip())
            for line in stdout.splitlines()
            if "custo:" in line
        ]
        self.assertGreaterEqual(len(custos), 2, stdout)
        self.assertLess(custos[-1], custos[0])

    def test_pesos_coerentes_com_funcao_geradora(self):
        """SC-007/FR-011: peso[0] > 0 e dominante, peso[1] < 0."""
        self._treinar_e_capturar_stdout()
        self.assertTrue(os.path.exists(self._caminho_modelo))
        with open(self._caminho_modelo, encoding="utf-8") as f:
            pesos = [float(p) for p in f.readline().split()]
        self.assertEqual(len(pesos), 4)
        self.assertGreater(pesos[0], 0.0)
        self.assertLess(pesos[1], 0.0)
        self.assertEqual(max(range(4), key=lambda j: abs(pesos[j])), 0)

