"""Teste de integracao da meta final: regressao_logistica.por (T028, US3, SC-005).

Valida que o .por de exemplo transpila e o .py gerado passa em py_compile,
roda o treinamento da regressao logistica e valida a acuracia final >= 0.95.
"""

import os
import random
import subprocess
import sys
import unittest

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
        self._caminho_csv = os.path.join(self._portugol_out, "dados.csv")
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
        """Gera dataset sintetico, executa o treino da regressao e valida acuracia."""
        os.makedirs(self._portugol_out, exist_ok=True)
        random.seed(42)
        with open(self._caminho_csv, "w", encoding="utf-8") as f:
            f.write("x1,x2,x3,x4,classe\n")
            for _ in range(500):
                x = [random.uniform(-3, 3) for _ in range(4)]
                z = 2.0 * x[0] - 1.0 * x[1] + 0.5 * x[2] - 0.3 * x[3] + 0.5
                y = 1 if z > 0.0 else 0
                f.write(",".join(map(str, x)) + f",{y}\n")

        r = _run_cli(CAMINHO_REG, "--run")
        self.assertEqual(r.returncode, 0, r.stderr)

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

