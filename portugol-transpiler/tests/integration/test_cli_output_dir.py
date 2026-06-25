"""Integracao da CLI com --output-dir e --run (US1/US2, conforme contracts/cli.md).

Cobre:
  - C2: --output-dir <tmpdir> gera .py e runtime no diretorio informado e o
    cria se ausente (FR-005, FR-008).
  - C3: --run gera e executa o .py com CWD no diretorio de saida, exibindo
    a saida do programa transpilado (SC-002, FR-002).
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT = os.path.join(PROJECT_DIR, "transpilador.py")
EXERCISES_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", "exercises_portugol"))
CAMINHO_MEDIA = os.path.join(EXERCISES_DIR, "01_media_nota.por")


def _run_cli(*args, cwd=PROJECT_DIR, stdin=None):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        input=stdin,
    )


class OutputDirCustomTest(unittest.TestCase):
    def test_gera_py_e_runtime_no_diretorio_custom(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "saida_custom")
            r = _run_cli(CAMINHO_MEDIA, "--output-dir", out_dir)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(out_dir, "01_media_nota.py")))
            self.assertTrue(
                os.path.exists(os.path.join(out_dir, "runtime_portugol.py"))
            )

    def test_cria_diretorio_ausente(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "aninhado", "portugol_out")
            self.assertFalse(os.path.exists(out_dir))
            r = _run_cli(CAMINHO_MEDIA, "--output-dir", out_dir)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.isdir(out_dir))
            self.assertTrue(os.path.exists(os.path.join(out_dir, "01_media_nota.py")))

    def test_diretorio_padrao_nao_e_tocado_com_output_dir_custom(self):
        with tempfile.TemporaryDirectory() as tmp:
            trabalho = os.path.join(tmp, "trabalho")
            os.makedirs(trabalho)
            out_custom = os.path.join(tmp, "custom")
            r = _run_cli(
                CAMINHO_MEDIA, "--output-dir", out_custom, cwd=trabalho
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(
                os.path.exists(os.path.join(trabalho, "portugol_out"))
            )
            self.assertTrue(os.path.exists(os.path.join(out_custom, "01_media_nota.py")))


class RunExecutaProgramaTest(unittest.TestCase):
    def test_run_gera_e_executa_com_sucesso(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "run_out")
            r = _run_cli(
                CAMINHO_MEDIA,
                "--run",
                "--output-dir",
                out_dir,
                stdin="8.0\n7.0\n",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(out_dir, "01_media_nota.py")))

    def test_run_executa_com_cwd_no_diretorio_de_saida(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "run_cwd")
            r = _run_cli(
                CAMINHO_MEDIA,
                "--run",
                "--output-dir",
                out_dir,
                stdin="8.0\n7.0\n",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(
                os.path.exists(os.path.join(out_dir, "runtime_portugol.py"))
            )

    def test_run_propaga_saida_do_programa(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "run_saida")
            r = _run_cli(
                CAMINHO_MEDIA,
                "--run",
                "--output-dir",
                out_dir,
                stdin="8.0\n7.0\n",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("média", r.stdout)


if __name__ == "__main__":
    unittest.main()
