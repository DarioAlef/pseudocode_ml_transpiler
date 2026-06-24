"""Contrato 1 (US2): a CLI principal responde a --help sem quebrar.

Espelha `contracts/cli-and-imports.md` -> Contrato 1 e o passo 2 do
quickstart.md. Cobre SC-002 e FR-009.
"""

import os
import subprocess
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "transpilador.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )


class CliHelpContratoTest(unittest.TestCase):
    def test_help_termina_com_exit_zero(self):
        result = _run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_help_exibe_mensagem_de_uso(self):
        result = _run_cli("--help")
        self.assertIn("transpilador.py", result.stdout)
        self.assertIn("arquivo", result.stdout)
        self.assertIn("--run", result.stdout)
        self.assertIn("--tokens", result.stdout)
        self.assertIn("--ast", result.stdout)

    def test_help_nao_lanca_traceback(self):
        result = _run_cli("--help")
        self.assertEqual(result.stderr, "")

    def test_sem_argumentos_nao_lanca_traceback(self):
        result = _run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
