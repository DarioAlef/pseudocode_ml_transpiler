"""Unit tests para seletividade de imports de runtime e não-interferência com math/random.

Testa que:
  - Imports from runtime_portugol aparecem se e somente se builtins de runtime são usados
  - Nenhuma duplicata em imports
  - Non-interference com math e random imports
"""

import unittest
from ast_nodes import CallExprNode, LiteralNode, ProgramNode, BlockNode, FunctionNode
from emissor import Emissor


def _programa_com_call(nome_builtin, args=None):
    """Programa com funcao inicio que chama `nome_builtin(args)`."""
    call = CallExprNode(
        callee=LiteralNode(kind="ident", value=nome_builtin),
        args=args or [],
    )
    inicio = FunctionNode(
        nome="inicio",
        tipo_retorno=None,
        params=[],
        body=BlockNode(stmts=[call]),
    )
    return ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")


def _programa_com_multiplas_calls(calls):
    """Programa com funcao inicio que chama multiplas funcoes."""
    inicio = FunctionNode(
        nome="inicio",
        tipo_retorno=None,
        params=[],
        body=BlockNode(stmts=calls),
    )
    return ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")


class TestSeletividadeImportsRuntime(unittest.TestCase):
    """Testa seletividade de imports de runtime (US2)."""

    def setUp(self):
        self.emissor = Emissor()

    def test_so_ler_csv_importa_ler_csv_sem_outros(self):
        """Programa com só ler_csv importa apenas ler_csv, não os outros."""
        args = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        programa = _programa_com_call("ler_csv", args)
        saida = self.emissor.gerar(programa)

        import_lines = [
            line for line in saida.split("\n")
            if "from runtime_portugol import" in line
        ]
        self.assertEqual(len(import_lines), 1, "Deve haver exatamente uma linha de import")
        import_line = import_lines[0]

        self.assertIn("ler_csv", import_line)
        self.assertNotIn("normalizar_zscore", import_line)
        self.assertNotIn("dividir_treino_teste", import_line)
        self.assertNotIn("salvar_pesos", import_line)
        self.assertNotIn("carregar_pesos", import_line)

    def test_programa_sem_builtins_runtime_sem_import(self):
        """Programa sem nenhum builtin de runtime não tem import from runtime_portugol."""
        args = [LiteralNode(kind="int", value="5")]
        programa = _programa_com_call("absoluto", args)
        saida = self.emissor.gerar(programa)

        self.assertNotIn("from runtime_portugol import", saida)

    def test_mesmo_builtin_usado_duas_vezes_sem_duplicata_em_import(self):
        """Mesmo builtin usado duas vezes aparece uma única vez no import."""
        args = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        call1 = CallExprNode(
            callee=LiteralNode(kind="ident", value="ler_csv"),
            args=args,
        )
        call2 = CallExprNode(
            callee=LiteralNode(kind="ident", value="ler_csv"),
            args=args,
        )
        programa = _programa_com_multiplas_calls([call1, call2])
        saida = self.emissor.gerar(programa)

        import_lines = [
            line for line in saida.split("\n")
            if "from runtime_portugol import" in line
        ]
        self.assertEqual(len(import_lines), 1)

        import_line = import_lines[0]
        ler_csv_count = import_line.count("ler_csv")
        self.assertEqual(ler_csv_count, 1, f"ler_csv aparece {ler_csv_count} vezes no import")


class TestNaoInterferenciaComMathRandom(unittest.TestCase):
    """Testa que imports de runtime não interferem com math/random."""

    def setUp(self):
        self.emissor = Emissor()

    def test_raiz_e_ler_csv_juntos(self):
        """Programa com raiz (math) e ler_csv (runtime) tem ambos os imports."""
        args_raiz = [LiteralNode(kind="int", value="4")]
        call_raiz = CallExprNode(
            callee=LiteralNode(kind="ident", value="raiz"),
            args=args_raiz,
        )

        args_ler = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        call_ler = CallExprNode(
            callee=LiteralNode(kind="ident", value="ler_csv"),
            args=args_ler,
        )

        programa = _programa_com_multiplas_calls([call_raiz, call_ler])
        saida = self.emissor.gerar(programa)

        self.assertIn("import math", saida)
        self.assertIn("from runtime_portugol import ler_csv", saida)

    def test_aleatorio_e_salvar_pesos_juntos(self):
        """Programa com aleatorio (random) e salvar_pesos (runtime) tem ambos os imports."""
        call_random = CallExprNode(
            callee=LiteralNode(kind="ident", value="aleatorio"),
            args=[],
        )

        args_salvar = [
            LiteralNode(kind="cadeia", value="modelo.txt"),
            LiteralNode(kind="ident", value="pesos"),
            LiteralNode(kind="ident", value="intercepto"),
        ]
        call_salvar = CallExprNode(
            callee=LiteralNode(kind="ident", value="salvar_pesos"),
            args=args_salvar,
        )

        programa = _programa_com_multiplas_calls([call_random, call_salvar])
        saida = self.emissor.gerar(programa)

        self.assertIn("import random", saida)
        self.assertIn("from runtime_portugol import salvar_pesos", saida)


if __name__ == "__main__":
    unittest.main()
