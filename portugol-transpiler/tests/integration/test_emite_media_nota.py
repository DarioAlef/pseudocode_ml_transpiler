"""Teste de integracao ponta-a-ponta: emitir 01_media_nota.por (T013, US1).

Cobre SC-001 (py_compile retorna 0), SC-002 (entrada 7.0/9.0 -> saida 8.0)
e SC-004 (ausencia de tabs no .py gerado).
"""

import os
import subprocess
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EXERCISES_DIR = os.path.abspath(os.path.join(PROJECT_DIR, "..", "exercises_portugol"))
CAMINHO_MEDIA = os.path.join(EXERCISES_DIR, "01_media_nota.por")
SAIDA_PY = os.path.join(PROJECT_DIR, "saida", "01_media_nota.py")


def _run_cli(*args, stdin=None):
    return subprocess.run(
        [sys.executable, "transpilador.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        input=stdin,
    )


class SC001CompilacaoTest(unittest.TestCase):
    def test_transpila_sem_erro(self):
        r = _run_cli(CAMINHO_MEDIA)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_py_compile_retorna_zero(self):
        _run_cli(CAMINHO_MEDIA)
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", SAIDA_PY],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)


class SC002ExecucaoTest(unittest.TestCase):
    def test_entrada_7_9_imprime_8(self):
        r = _run_cli(CAMINHO_MEDIA, "--run", stdin="7.0\n9.0\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("8.0", r.stdout)

    def test_saida_contem_media(self):
        r = _run_cli(CAMINHO_MEDIA, "--run", stdin="7.0\n9.0\n")
        self.assertIn("média", r.stdout)


class SC004SemTabsTest(unittest.TestCase):
    def test_py_gerado_nao_contem_tabs(self):
        _run_cli(CAMINHO_MEDIA)
        with open(SAIDA_PY, encoding="utf-8") as f:
            conteudo = f.read()
        self.assertNotIn("\t", conteudo)

    def test_indentacao_em_multiplos_de_4(self):
        _run_cli(CAMINHO_MEDIA)
        with open(SAIDA_PY, encoding="utf-8") as f:
            linhas = f.readlines()
        for ln in linhas:
            if ln.startswith(" "):
                espacos = len(ln) - len(ln.lstrip(" "))
                self.assertEqual(espacos % 4, 0, f"indentacao nao mult. de 4: {ln!r}")


if __name__ == "__main__":
    unittest.main()
