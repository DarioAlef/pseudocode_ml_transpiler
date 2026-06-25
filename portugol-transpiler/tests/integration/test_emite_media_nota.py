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
SAIDA_PY = os.path.join(PROJECT_DIR, "portugol_out", "01_media_nota.py")


def _run_cli(*args, stdin=None):
    """Executa a CLI transpilador.py com argumentos."""
    return subprocess.run(
        [sys.executable, "transpilador.py", *args],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        input=stdin,
    )


class SC001CompilacaoTest(unittest.TestCase):
    """Suite de testes integrados para compilacao e verificacao basica do media_nota."""

    def setUp(self):
        """Limpa o arquivo gerado antes de iniciar."""
        self._limpar_arquivos()

    def tearDown(self):
        """Limpa o arquivo gerado ao finalizar."""
        self._limpar_arquivos()

    def _limpar_arquivos(self):
        """Deleta o arquivo Python gerado se existir."""
        if os.path.exists(SAIDA_PY):
            os.unlink(SAIDA_PY)

    def test_transpila_sem_erro(self):
        """Valida se a transpilação ocorre com retorno de sucesso."""
        r = _run_cli(CAMINHO_MEDIA)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_py_compile_retorna_zero(self):
        """Valida se a compilação do arquivo gerado tem sintaxe correta."""
        _run_cli(CAMINHO_MEDIA)
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", SAIDA_PY],
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)


class SC002ExecucaoTest(unittest.TestCase):
    """Suite de testes integrados para validar a execucao do media_nota."""

    def test_entrada_7_9_imprime_8(self):
        """Valida que entradas 7.0 e 9.0 produzem a media 8.0 na saida."""
        r = _run_cli(CAMINHO_MEDIA, "--run", stdin="7.0\n9.0\n")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("8.0", r.stdout)

    def test_saida_contem_media(self):
        """Valida que a saida contem a palavra media."""
        r = _run_cli(CAMINHO_MEDIA, "--run", stdin="7.0\n9.0\n")
        self.assertIn("média", r.stdout)


class SC004SemTabsTest(unittest.TestCase):
    """Suite de testes para validar a qualidade de formatacao e indentacao."""

    def setUp(self):
        """Limpa o arquivo gerado antes do teste."""
        if os.path.exists(SAIDA_PY):
            os.unlink(SAIDA_PY)

    def tearDown(self):
        """Limpa o arquivo gerado apos o teste."""
        if os.path.exists(SAIDA_PY):
            os.unlink(SAIDA_PY)

    def test_py_gerado_nao_contem_tabs(self):
        """Valida que o arquivo gerado nao possui caracteres tabulacao."""
        _run_cli(CAMINHO_MEDIA)
        with open(SAIDA_PY, encoding="utf-8") as f:
            conteudo = f.read()
        self.assertNotIn("\t", conteudo)

    def test_indentacao_em_multiplos_de_4(self):
        """Valida que todos os recuos de espaco sao multiplos de 4."""
        _run_cli(CAMINHO_MEDIA)
        with open(SAIDA_PY, encoding="utf-8") as f:
            linhas = f.readlines()
        for ln in linhas:
            if ln.startswith(" "):
                espacos = len(ln) - len(ln.lstrip(" "))
                self.assertEqual(espacos % 4, 0, f"indentacao nao mult. de 4: {ln!r}")



if __name__ == "__main__":
    unittest.main()
