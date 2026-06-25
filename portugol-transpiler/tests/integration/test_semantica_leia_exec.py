"""Teste de integracao US3 (Card 13): diagnosticos nao-fatais via CLI.

Cobre SC-006/SC-007: variavel nao declarada (aviso) e aridade errada (erro)
sao reportados em stderr, mas a transpilacao prossegue e o .py e gerado.
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_PROG = """programa {
  funcao real soma(real a, real b) {
    retorne a + b
  }
  funcao inicio() {
    real x
    x = y + 1
    escreval(soma(1.0))
  }
}"""


class SemanticaNaoFatalTest(unittest.TestCase):
    def test_diagnosticos_em_stderr_mas_gera_py(self):
        with tempfile.TemporaryDirectory() as tmp:
            por = os.path.join(tmp, "sem.por")
            with open(por, "w", encoding="utf-8") as f:
                f.write(_PROG)
            out_dir = os.path.join(tmp, "out")
            r = subprocess.run(
                [sys.executable, "transpilador.py", por, "--output-dir", out_dir],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("aviso", r.stderr)
            self.assertIn("y", r.stderr)
            self.assertIn("erro", r.stderr)
            self.assertIn("soma", r.stderr)
            self.assertTrue(os.path.exists(os.path.join(out_dir, "sem.py")))


if __name__ == "__main__":
    unittest.main()
