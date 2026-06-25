"""Contrato da CLI de transpilacao (T012, US1, conforme contracts/cli_transpilar.md).

Cobre: gerar cria saida/<nome>.py e copia runtime_portugol.py; erro sintatico
-> mensagem com linha/coluna em stderr e retorno 1.
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXERCISES_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", "exercises_portugol"))
CAMINHO_MEDIA = os.path.join(EXERCISES_DIR, "01_media_nota.por")


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "transpilador.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )


class GeracaoTest(unittest.TestCase):
    def setUp(self):
        self._saida_py = os.path.join(PROJECT_DIR, "saida", "01_media_nota.py")
        self._saida_runtime = os.path.join(PROJECT_DIR, "saida", "runtime_portugol.py")
        if os.path.exists(self._saida_py):
            os.unlink(self._saida_py)
        if os.path.exists(self._saida_runtime):
            os.unlink(self._saida_runtime)

    def test_gera_arquivo_py(self):
        r = _run_cli(CAMINHO_MEDIA)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(self._saida_py))

    def test_copia_runtime_portugol(self):
        r = _run_cli(CAMINHO_MEDIA)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(self._saida_runtime))

    def test_imprime_caminho_no_stdout(self):
        r = _run_cli(CAMINHO_MEDIA)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("01_media_nota.py", r.stdout)


class ErroSintaticoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".por", delete=False, encoding="utf-8"
        )
        self._tmp.write("programa { funcao inicio( }")
        self._tmp.close()

    def tearDown(self):
        os.unlink(self._tmp.name)

    def test_retorno_um_em_erro_sintatico(self):
        r = _run_cli(self._tmp.name)
        self.assertEqual(r.returncode, 1)

    def test_stderr_contem_linha(self):
        r = _run_cli(self._tmp.name)
        self.assertIn("linha", r.stderr)

    def test_stderr_contem_coluna(self):
        r = _run_cli(self._tmp.name)
        self.assertIn("coluna", r.stderr)


if __name__ == "__main__":
    unittest.main()
