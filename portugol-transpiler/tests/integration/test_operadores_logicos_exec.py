"""Teste de integracao US1 (Card 10): palavra e simbolo executam igual.

Cobre SC-002 ponta-a-ponta: transpila e executa via CLI dois programas
equivalentes (e/ou/nao vs &&/||/!) e compara a saida.
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

_PALAVRAS = """programa {
  funcao inicio() {
    inteiro x = 1
    inteiro y = 1
    se (x > 0 e y > 0) { escreval("AMBOS") }
    se (nao (x > 5)) { escreval("PEQUENO") }
  }
}"""

_SIMBOLOS = """programa {
  funcao inicio() {
    inteiro x = 1
    inteiro y = 1
    se (x > 0 && y > 0) { escreval("AMBOS") }
    se (!(x > 5)) { escreval("PEQUENO") }
  }
}"""


def _transpilar_e_rodar(fonte):
    """Escreve a fonte num .por temporario, roda via CLI e devolve o stdout."""
    with tempfile.TemporaryDirectory() as tmp:
        por = os.path.join(tmp, "prog.por")
        with open(por, "w", encoding="utf-8") as f:
            f.write(fonte)
        out_dir = os.path.join(tmp, "out")
        r = subprocess.run(
            [sys.executable, "transpilador.py", por, "--run", "--output-dir", out_dir],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        return r


class OperadoresLogicosExecTest(unittest.TestCase):
    def test_palavras_executam(self):
        r = _transpilar_e_rodar(_PALAVRAS)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("AMBOS", r.stdout)
        self.assertIn("PEQUENO", r.stdout)

    def test_palavra_equivale_simbolo(self):
        rp = _transpilar_e_rodar(_PALAVRAS)
        rs = _transpilar_e_rodar(_SIMBOLOS)
        self.assertEqual(rp.returncode, 0, rp.stderr)
        self.assertEqual(rs.returncode, 0, rs.stderr)
        linhas_p = [ln for ln in rp.stdout.splitlines() if ln in ("AMBOS", "PEQUENO")]
        linhas_s = [ln for ln in rs.stdout.splitlines() if ln in ("AMBOS", "PEQUENO")]
        self.assertEqual(linhas_p, linhas_s)


if __name__ == "__main__":
    unittest.main()
