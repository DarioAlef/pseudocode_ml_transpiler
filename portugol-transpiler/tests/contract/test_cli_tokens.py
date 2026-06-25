"""Contrato do modo --tokens da CLI (US6, espelha contracts/cli.md -> C4).

Cobre T1 (impressao de tokens), T2 (01_media_nota.por exit 0 e tokens
esperados, SC-004), T3 (erro lexico em stderr com exit != 0), T4
(compatibilidade com o scaffold: --help preservado) e a garantia de que
--tokens NAO grava nenhum .py em portugol_out/ (SC-003, FR-003).
"""

import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

EXERCICIO = os.path.abspath(
    os.path.join(PROJECT_DIR, "..", "exercises_portugol", "01_media_nota.por")
)


def _run_cli(*args):
    return subprocess.run(
        [sys.executable, "transpilador.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
    )


class NaoGravaArquivoTest(unittest.TestCase):
    def setUp(self):
        self._out_dir = os.path.join(PROJECT_DIR, "portugol_out")
        if os.path.isdir(self._out_dir):
            for nome in os.listdir(self._out_dir):
                if nome.endswith(".py"):
                    os.unlink(os.path.join(self._out_dir, nome))

    def test_tokens_nao_gera_py(self):
        r = _run_cli(EXERCICIO, "--tokens")
        self.assertEqual(r.returncode, 0, r.stderr)
        if os.path.isdir(self._out_dir):
            pys = [n for n in os.listdir(self._out_dir) if n.endswith(".py")]
            self.assertEqual(pys, [])


class T1ImpressaoTokensTest(unittest.TestCase):
    def test_imprime_tipo_e_valor_dos_tokens(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".por", delete=False, encoding="utf-8"
        ) as f:
            f.write("inteiro x = 42")
            caminho = f.name
        try:
            result = _run_cli(caminho, "--tokens")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("INTEIRO", result.stdout)
            self.assertIn("INT_LIT", result.stdout)
            self.assertIn("42", result.stdout)
            self.assertIn("EOF", result.stdout)
        finally:
            os.unlink(caminho)

    def test_saida_termina_com_eof(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".por", delete=False, encoding="utf-8"
        ) as f:
            f.write("real y")
            caminho = f.name
        try:
            result = _run_cli(caminho, "--tokens")
            self.assertEqual(result.returncode, 0, result.stderr)
            linhas = [ln for ln in result.stdout.splitlines() if ln.strip()]
            self.assertIn("EOF", linhas[-1])
        finally:
            os.unlink(caminho)


class T2MediaNotaEndToEndTest(unittest.TestCase):
    def test_media_nota_exit_zero_sem_erro(self):
        result = _run_cli(EXERCICIO, "--tokens")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_media_nota_imprime_tokens_esperados(self):
        result = _run_cli(EXERCICIO, "--tokens")
        self.assertEqual(result.returncode, 0, result.stderr)
        for tipo in [
            "PROGRAMA",
            "FUNCAO",
            "INICIO",
            "REAL",
            "STRING_LIT",
            "ASSIGN",
            "MAIS",
            "DIV",
            "EOF",
        ]:
            with self.subTest(tipo=tipo):
                self.assertIn(tipo, result.stdout)
        self.assertIn("escreva", result.stdout)
        self.assertIn("leia", result.stdout)


class T3ErroLexicoTest(unittest.TestCase):
    def test_caractere_ilegal_em_stderr_e_exit_nao_zero(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".por", delete=False, encoding="utf-8"
        ) as f:
            f.write("inteiro @ x")
            caminho = f.name
        try:
            result = _run_cli(caminho, "--tokens")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("linha", result.stderr.lower())
            self.assertIn("coluna", result.stderr.lower())
        finally:
            os.unlink(caminho)

    def test_cadeia_nao_terminada_em_stderr(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".por", delete=False, encoding="utf-8"
        ) as f:
            f.write('"abc')
            caminho = f.name
        try:
            result = _run_cli(caminho, "--tokens")
            self.assertNotEqual(result.returncode, 0)
            self.assertGreater(len(result.stderr), 0)
        finally:
            os.unlink(caminho)


class T4CompatibilidadeScaffoldTest(unittest.TestCase):
    def test_help_preservado(self):
        result = _run_cli("--help")
        self.assertEqual(result.returncode, 0)
        for flag in ["--run", "--tokens", "--ast", "arquivo"]:
            with self.subTest(flag=flag):
                self.assertIn(flag, result.stdout)

    def test_superficie_de_argumentos_preservada(self):
        result = _run_cli("--help")
        self.assertIn("transpilador.py", result.stdout)


if __name__ == "__main__":
    unittest.main()
