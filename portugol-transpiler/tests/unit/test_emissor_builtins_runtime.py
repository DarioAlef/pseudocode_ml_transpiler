"""Unit tests para mapeamento de builtins de runtime e agregação de imports.

Testa que cada um dos 5 builtins de runtime (ler_csv, normalizar_zscore,
dividir_treino_teste, salvar_pesos, carregar_pesos) é reconhecido pelo
emissor, gera chamadas posicionais idênticas e adiciona o import seletivo.
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


class TestEmissorBuiltinsRuntime(unittest.TestCase):
    """Testa mapeamento de builtins de runtime: reconhecimento e emissão."""

    def setUp(self):
        self.emissor = Emissor()

    def test_ler_csv_mapeado_e_importado(self):
        """ler_csv("dados.csv", X, y) gera chamada e import corretos."""
        args = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        programa = _programa_com_call("ler_csv", args)
        saida = self.emissor.gerar(programa)
        self.assertIn('ler_csv("dados.csv", X, y)', saida)
        self.assertIn("from runtime_portugol import ler_csv", saida)

    def test_normalizar_zscore_mapeado_e_importado(self):
        """normalizar_zscore(X, N, NUM_FEATURES) gera chamada e import corretos."""
        args = [
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="N"),
            LiteralNode(kind="ident", value="NUM_FEATURES"),
        ]
        programa = _programa_com_call("normalizar_zscore", args)
        saida = self.emissor.gerar(programa)
        self.assertIn("normalizar_zscore(X, N, NUM_FEATURES)", saida)
        self.assertIn("from runtime_portugol import normalizar_zscore", saida)

    def test_dividir_treino_teste_mapeado_e_importado(self):
        """dividir_treino_teste(X, y, frac) gera chamada e import corretos."""
        args = [
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
            LiteralNode(kind="ident", value="frac"),
        ]
        programa = _programa_com_call("dividir_treino_teste", args)
        saida = self.emissor.gerar(programa)
        self.assertIn("dividir_treino_teste(X, y, frac)", saida)
        self.assertIn("from runtime_portugol import dividir_treino_teste", saida)

    def test_salvar_pesos_mapeado_e_importado(self):
        """salvar_pesos("modelo.txt", pesos, intercepto) gera chamada e import corretos."""
        args = [
            LiteralNode(kind="cadeia", value="modelo.txt"),
            LiteralNode(kind="ident", value="pesos"),
            LiteralNode(kind="ident", value="intercepto"),
        ]
        programa = _programa_com_call("salvar_pesos", args)
        saida = self.emissor.gerar(programa)
        self.assertIn('salvar_pesos("modelo.txt", pesos, intercepto)', saida)
        self.assertIn("from runtime_portugol import salvar_pesos", saida)

    def test_carregar_pesos_mapeado_e_importado(self):
        """carregar_pesos("modelo.txt") gera chamada e import corretos."""
        args = [
            LiteralNode(kind="cadeia", value="modelo.txt"),
        ]
        programa = _programa_com_call("carregar_pesos", args)
        saida = self.emissor.gerar(programa)
        self.assertIn('carregar_pesos("modelo.txt")', saida)
        self.assertIn("from runtime_portugol import carregar_pesos", saida)


class TestAgregacaoImportsRuntime(unittest.TestCase):
    """Testa que múltiplos builtins de runtime agregam imports corretamente."""

    def setUp(self):
        self.emissor = Emissor()

    def test_tres_builtins_diferentes_import_unico_ordenado(self):
        """Três builtins distintos geram UMA ÚNICA linha de import, ordenados."""
        args_ler = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        call_ler = CallExprNode(
            callee=LiteralNode(kind="ident", value="ler_csv"),
            args=args_ler,
        )

        args_norm = [
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="N"),
            LiteralNode(kind="ident", value="NUM_FEATURES"),
        ]
        call_norm = CallExprNode(
            callee=LiteralNode(kind="ident", value="normalizar_zscore"),
            args=args_norm,
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

        programa = _programa_com_multiplas_calls([call_ler, call_norm, call_salvar])
        saida = self.emissor.gerar(programa)

        import_lines = [
            line for line in saida.split("\n")
            if "from runtime_portugol import" in line
        ]
        self.assertEqual(
            len(import_lines),
            1,
            f"Esperava 1 linha de import, encontrou {len(import_lines)}",
        )

        import_line = import_lines[0]
        self.assertIn("from runtime_portugol import", import_line)
        self.assertTrue(
            "ler_csv" in import_line and "normalizar_zscore" in import_line and "salvar_pesos" in import_line,
            f"Import incompleto ou não ordenado: {import_line}"
        )

    def test_mesmo_builtin_duas_vezes_sem_duplicata(self):
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


if __name__ == "__main__":
    unittest.main()
