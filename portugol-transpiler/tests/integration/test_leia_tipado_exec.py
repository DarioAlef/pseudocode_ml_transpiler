"""Teste de integracao US4 (Card 12): leia tipado e multi-arg via CLI.

Cobre FR-018/FR-021 ponta-a-ponta: leia(idade, nota) le da stdin e converte
para int/float, preservando os tipos na execucao.
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_PROG = """programa {
  funcao inicio() {
    inteiro idade
    real nota
    leia(idade, nota)
    escreval(idade)
    escreval(nota)
  }
}"""


class LeiaTipadoExecTest(unittest.TestCase):
    def test_le_inteiro_e_real(self):
        with tempfile.TemporaryDirectory() as tmp:
            por = os.path.join(tmp, "leitura.por")
            with open(por, "w", encoding="utf-8") as f:
                f.write(_PROG)
            out_dir = os.path.join(tmp, "out")
            r = subprocess.run(
                [sys.executable, "transpilador.py", por, "--run",
                 "--output-dir", out_dir],
                cwd=PROJECT_DIR,
                capture_output=True,
                text=True,
                input="30\n8.5\n",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            linhas = r.stdout.splitlines()
            self.assertIn("30", linhas)
            self.assertIn("8.5", linhas)


if __name__ == "__main__":
    unittest.main()
