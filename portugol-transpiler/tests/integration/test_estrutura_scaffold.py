"""Integracao (US1): o esqueleto completo do projeto existe nos lugares certos.

Cobre os criterios de aceite da User Story 1 (spec.md) e os passos 1 e 4
do quickstart.md:
- SC-001: 100% dos arquivos/diretorios previstos na Seção 5 existem.
- SC-004 / FR-003: 100% dos modulos Python tem docstring de cabecalho.
- FR-004..FR-008: exemplos, tests/, README, requirements e .gitignore.
"""

import importlib
import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MODULOS = [
    "transpilador.py",
    "lexer.py",
    "parser.py",
    "ast_nodes.py",
    "emissor.py",
    "runtime_portugol.py",
]

DIRETORIOS = ["exemplos", "tests"]

EXEMPLOS = [
    os.path.join("exemplos", "regressao_logistica.por"),
    os.path.join("exemplos", "dados.csv"),
]

APOIO = ["README.md", "requirements.txt", ".gitignore"]


class EstruturaScaffoldTest(unittest.TestCase):
    """Valida que o esqueleto do projeto (US1) esta completo."""

    def test_modulos_do_pipeline_existem(self):
        for nome in MODULOS:
            with self.subTest(modulo=nome):
                self.assertTrue(
                    os.path.isfile(os.path.join(PROJECT_DIR, nome)),
                    f"Modulo esperado ausente: {nome}",
                )

    def test_diretorios_previstos_existem(self):
        for caminho in DIRETORIOS:
            with self.subTest(dir=caminho):
                self.assertTrue(
                    os.path.isdir(os.path.join(PROJECT_DIR, caminho)),
                    f"Diretorio esperado ausente: {caminho}",
                )

    def test_exemplos_placeholder_existem(self):
        for rel in EXEMPLOS:
            with self.subTest(arquivo=rel):
                self.assertTrue(
                    os.path.isfile(os.path.join(PROJECT_DIR, rel)),
                    f"Exemplo esperado ausente: {rel}",
                )

    def test_arquivos_de_apoio_existem(self):
        for nome in APOIO:
            with self.subTest(arquivo=nome):
                self.assertTrue(
                    os.path.isfile(os.path.join(PROJECT_DIR, nome)),
                    f"Arquivo de apoio esperado ausente: {nome}",
                )

    def test_requirements_txt_vazio(self):
        with open(os.path.join(PROJECT_DIR, "requirements.txt"), "rb") as f:
            conteudo = f.read()
        self.assertEqual(
            conteudo.strip(),
            b"",
            "requirements.txt deve estar vazio (apenas stdlib nesta fase)",
        )

    def test_gitignore_contem_padroes_obrigatorios(self):
        with open(os.path.join(PROJECT_DIR, ".gitignore"), encoding="utf-8") as f:
            conteudo = f.read()
        for padrao in ["__pycache__", "*.pyc", "portugol_out"]:
            with self.subTest(padrao=padrao):
                self.assertIn(padrao, conteudo)

    def test_readme_contem_comando_de_uso_basico(self):
        with open(os.path.join(PROJECT_DIR, "README.md"), encoding="utf-8") as f:
            conteudo = f.read()
        self.assertIn("python transpilador.py", conteudo)

    def test_csv_placeholder_tem_cabecalho_e_rotulo(self):
        with open(
            os.path.join(PROJECT_DIR, "exemplos", "dados.csv"), encoding="utf-8"
        ) as f:
            linhas = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
        self.assertGreaterEqual(len(linhas), 2, "dados.csv precisa de cabecalho + 1 linha")
        cabecalho = linhas[0].split(",")
        self.assertEqual(cabecalho[-1].strip().lower(), "classe")
        ultima_coluna = linhas[1].split(",")[-1].strip()
        self.assertIn(ultima_coluna, {"0", "1"})

    def test_modulos_tem_docstring_de_cabecalho_nao_vazio(self):
        sys_path_original = sys.path[:]
        sys.path.insert(0, PROJECT_DIR)
        try:
            for nome in [
                "transpilador",
                "lexer",
                "parser",
                "ast_nodes",
                "emissor",
                "runtime_portugol",
            ]:
                with self.subTest(modulo=nome):
                    mod = importlib.import_module(nome)
                    self.assertTrue(
                        mod.__doc__ and mod.__doc__.strip(),
                        f"Modulo {nome} sem docstring de cabecalho",
                    )
        finally:
            sys.path[:] = sys_path_original


if __name__ == "__main__":
    unittest.main()
