"""Teste de integracao da meta final: regressao_logistica.por (T028, US3, SC-005).

Valida que o .por de exemplo transpila e o .py gerado passa em py_compile.
"""

import os
import subprocess
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAMINHO_REG = os.path.join(PROJECT_DIR, "exemplos", "regressao_logistica.por")
SAIDA_PY = os.path.join(PROJECT_DIR, "saida", "regressao_logistica.py")


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "transpilador.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )


class SC005RegressaoCompilaTest(unittest.TestCase):
    def test_transpila_sem_erro(self):
        r = _run_cli(CAMINHO_REG)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_py_gerado_existe(self):
        _run_cli(CAMINHO_REG)
        self.assertTrue(os.path.exists(SAIDA_PY))

    def test_py_compile_retorna_zero(self):
        _run_cli(CAMINHO_REG)
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", SAIDA_PY],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_primeira_linha_e_cabecalho(self):
        _run_cli(CAMINHO_REG)
        with open(SAIDA_PY, encoding="utf-8") as f:
            primeira = f.readline().rstrip("\n")
        self.assertEqual(primeira, "# GERADO AUTOMATICAMENTE — NÃO EDITE")

    def test_sem_tabs_no_gerado(self):
        _run_cli(CAMINHO_REG)
        with open(SAIDA_PY, encoding="utf-8") as f:
            conteudo = f.read()
        self.assertNotIn("\t", conteudo)

    def test_imports_seletivos_runtime_e_math(self):
        _run_cli(CAMINHO_REG)
        with open(SAIDA_PY, encoding="utf-8") as f:
            conteudo = f.read()
        self.assertIn("from runtime_portugol import", conteudo)
        self.assertIn("import math", conteudo)


if __name__ == "__main__":
    unittest.main()
