"""Teste de integracao US2 (Card 11): '^' executa via CLI.

Cobre SC-003 ponta-a-ponta: 'real x = 2 ^ 10' gera 'x = 2 ** 10' e imprime 1024.
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_PROG = """programa {
  funcao inicio() {
    real x = 2 ^ 10
    escreval(x)
  }
}"""


class PotenciaExecTest(unittest.TestCase):
    def test_2_pot_10_imprime_1024(self):
        with tempfile.TemporaryDirectory() as tmp:
            por = os.path.join(tmp, "pot.por")
            with open(por, "w", encoding="utf-8") as f:
                f.write(_PROG)
            out_dir = os.path.join(tmp, "out")
            r = subprocess.run(
                [sys.executable, "transpilador.py", por, "--run",
                 "--output-dir", out_dir],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("1024", r.stdout)
            py = os.path.join(out_dir, "pot.py")
            with open(py, encoding="utf-8") as f:
                conteudo = f.read()
            self.assertIn("**", conteudo)


if __name__ == "__main__":
    unittest.main()
