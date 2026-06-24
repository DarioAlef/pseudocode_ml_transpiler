"""Contrato 2 (US2): os modulos do pipeline sao importaveis em conjunto.

Espelha `contracts/cli-and-imports.md` -> Contrato 2 e o passo 3 do
quickstart.md. Cobre SC-003 e FR-010.
"""

import os
import subprocess
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MODULOS = ["lexer", "parser", "ast_nodes", "emissor", "runtime_portugol"]


class ImportsContratoTest(unittest.TestCase):
    def test_import_conjunto_dos_modulos_exit_zero(self):
        result = subprocess.run(
            [sys.executable, "-c", "import lexer, parser, ast_nodes, emissor, runtime_portugol"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_cada_modulo_importavel_individualmente(self):
        for nome in MODULOS:
            with self.subTest(modulo=nome):
                result = subprocess.run(
                    [sys.executable, "-c", f"import {nome}"],
                    cwd=PROJECT_DIR,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
