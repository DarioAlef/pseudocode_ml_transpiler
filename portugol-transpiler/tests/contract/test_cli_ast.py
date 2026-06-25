"""Contrato da acao --ast da CLI (US3, FR-004/SC-004, espelha contracts/cli.md -> C5).

Cobre: sucesso -> stdout indentado nao vazio + exit 0;
erro sintatico -> stderr com linha/coluna + exit 1;
alem disso, --ast NAO grava nenhum .py em portugol_out/.
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_TRANSPILER = PROJECT_DIR
EXERCISES_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", "exercises_portugol"))
CAMINHO_MEDIA = os.path.join(EXERCISES_DIR, "01_media_nota.por")


def _run(args):
    return subprocess.run(
        [sys.executable, "transpilador.py"] + args,
        capture_output=True,
        text=True,
        cwd=DIR_TRANSPILER,
    )


class NaoGravaArquivoTest(unittest.TestCase):
    def setUp(self):
        self._out_dir = os.path.join(PROJECT_DIR, "portugol_out")
        if os.path.isdir(self._out_dir):
            for nome in os.listdir(self._out_dir):
                if nome.endswith(".py"):
                    os.unlink(os.path.join(self._out_dir, nome))

    def test_ast_nao_gera_py(self):
        r = _run([CAMINHO_MEDIA, "--ast"])
        self.assertEqual(r.returncode, 0, r.stderr)
        if os.path.isdir(self._out_dir):
            pys = [n for n in os.listdir(self._out_dir) if n.endswith(".py")]
            self.assertEqual(pys, [])


class AstSucessoTest(unittest.TestCase):
    def test_exit_zero(self):
        r = _run([CAMINHO_MEDIA, "--ast"])
        self.assertEqual(r.returncode, 0)

    def test_stdout_nao_vazio(self):
        r = _run([CAMINHO_MEDIA, "--ast"])
        self.assertGreater(len(r.stdout.strip()), 0)

    def test_stdout_contem_ProgramNode(self):
        r = _run([CAMINHO_MEDIA, "--ast"])
        self.assertIn("ProgramNode", r.stdout)

    def test_stderr_vazio_em_sucesso(self):
        r = _run([CAMINHO_MEDIA, "--ast"])
        self.assertEqual(r.stderr.strip(), "")


class AstErroSintaticoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".por", delete=False, encoding="utf-8"
        )
        self._tmp.write("programa { funcao inicio( }")
        self._tmp.close()

    def tearDown(self):
        os.unlink(self._tmp.name)

    def test_exit_um_em_erro(self):
        r = _run([self._tmp.name, "--ast"])
        self.assertEqual(r.returncode, 1)

    def test_stderr_contem_linha(self):
        r = _run([self._tmp.name, "--ast"])
        self.assertIn("linha", r.stderr)

    def test_stderr_contem_coluna(self):
        r = _run([self._tmp.name, "--ast"])
        self.assertIn("coluna", r.stderr)

    def test_stdout_vazio_em_erro(self):
        r = _run([self._tmp.name, "--ast"])
        self.assertEqual(r.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
