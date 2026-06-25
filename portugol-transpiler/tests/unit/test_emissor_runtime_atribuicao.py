"""Unit tests para atribuição escalar, uso como statement e global em builtins de runtime.

Testa que:
  - Atribuição escalar: N = ler_csv(...) emite corretamente
  - Uso como statement: normalizar_zscore(...) emite sem atribuição
  - Diretiva global: dentro de função, usar global N antes da atribuição
"""

import unittest
from ast_nodes import (
    AssignNode,
    BlockNode,
    CallExprNode,
    FunctionNode,
    LiteralNode,
    ProgramNode,
    TypeNode,
    VarDeclNode,
)
from emissor import Emissor


def _programa_com_stmt(stmts):
    """Programa com funcao inicio contendo os statements."""
    inicio = FunctionNode(
        nome="inicio",
        tipo_retorno=None,
        params=[],
        body=BlockNode(stmts=stmts),
    )
    return ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")


def _programa_com_funcao_e_inicio(funcoes, inicio_stmts):
    """Programa com funcoes adicionais e a funcao inicio."""
    inicio = FunctionNode(
        nome="inicio",
        tipo_retorno=None,
        params=[],
        body=BlockNode(stmts=inicio_stmts),
    )
    return ProgramNode(funcoes=funcoes + [inicio], globais=[], dialeto="portugol_studio")


class TestAtribuicaoEscalarRuntime(unittest.TestCase):
    """Testa atribuição escalar com chamada de builtin de runtime (US3, T010)."""

    def setUp(self):
        self.emissor = Emissor()

    def test_n_ler_csv_gera_atribuicao(self):
        """N = ler_csv("dados.csv", X, y) gera a atribuição escalar."""
        args = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        call = CallExprNode(
            callee=LiteralNode(kind="ident", value="ler_csv"),
            args=args,
        )
        assign = AssignNode(
            alvo=LiteralNode(kind="ident", value="N"),
            valor=call,
        )
        programa = _programa_com_stmt([assign])
        saida = self.emissor.gerar(programa)

        self.assertIn('N = ler_csv("dados.csv", X, y)', saida)
        self.assertIn("from runtime_portugol import ler_csv", saida)

    def test_x_dividir_treino_teste_gera_atribuicao(self):
        """X_tr = dividir_treino_teste(...) gera atribuição."""
        args = [
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
            LiteralNode(kind="real", value="0.2"),
        ]
        call = CallExprNode(
            callee=LiteralNode(kind="ident", value="dividir_treino_teste"),
            args=args,
        )
        assign = AssignNode(
            alvo=LiteralNode(kind="ident", value="X_tr"),
            valor=call,
        )
        programa = _programa_com_stmt([assign])
        saida = self.emissor.gerar(programa)

        self.assertIn("X_tr = dividir_treino_teste(X, y, 0.2)", saida)
        self.assertIn("from runtime_portugol import dividir_treino_teste", saida)


class TestStatementRuntime(unittest.TestCase):
    """Testa uso como statement sem atribuição (US3, T011)."""

    def setUp(self):
        self.emissor = Emissor()

    def test_normalizar_zscore_como_statement(self):
        """normalizar_zscore(X, N, NUM_FEATURES) como statement gera chamada sem atribuição."""
        args = [
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="N"),
            LiteralNode(kind="ident", value="NUM_FEATURES"),
        ]
        call = CallExprNode(
            callee=LiteralNode(kind="ident", value="normalizar_zscore"),
            args=args,
        )
        programa = _programa_com_stmt([call])
        saida = self.emissor.gerar(programa)

        self.assertIn("normalizar_zscore(X, N, NUM_FEATURES)", saida)
        self.assertNotIn("= normalizar_zscore", saida)
        self.assertIn("from runtime_portugol import normalizar_zscore", saida)

    def test_salvar_pesos_como_statement(self):
        """salvar_pesos(...) como statement gera chamada sem atribuição."""
        args = [
            LiteralNode(kind="cadeia", value="modelo.txt"),
            LiteralNode(kind="ident", value="pesos"),
            LiteralNode(kind="ident", value="intercepto"),
        ]
        call = CallExprNode(
            callee=LiteralNode(kind="ident", value="salvar_pesos"),
            args=args,
        )
        programa = _programa_com_stmt([call])
        saida = self.emissor.gerar(programa)

        self.assertIn('salvar_pesos("modelo.txt", pesos, intercepto)', saida)
        self.assertNotIn("= salvar_pesos", saida)
        self.assertIn("from runtime_portugol import salvar_pesos", saida)


class TestGlobalDirectiveRuntime(unittest.TestCase):
    """Testa diretiva global em funções que modificam globais (US3, T012)."""

    def setUp(self):
        self.emissor = Emissor()

    def test_global_n_em_funcao_com_atribuicao_ler_csv(self):
        """Função que faz N = ler_csv(...) emite global N."""
        args = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        call = CallExprNode(
            callee=LiteralNode(kind="ident", value="ler_csv"),
            args=args,
        )
        assign = AssignNode(
            alvo=LiteralNode(kind="ident", value="N"),
            valor=call,
        )

        funcao = FunctionNode(
            nome="carregar_dados",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[assign]),
        )

        inicio = FunctionNode(
            nome="inicio",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[]),
        )

        global_n = VarDeclNode(
            tipo=TypeNode(base="inteiro", is_array=False),
            nome="N",
        )

        programa = ProgramNode(
            funcoes=[funcao, inicio],
            globais=[global_n],
            dialeto="portugol_studio",
        )

        saida = self.emissor.gerar(programa)

        self.assertIn("global N", saida)
        self.assertIn('N = ler_csv("dados.csv", X, y)', saida)
        self.assertIn("from runtime_portugol import ler_csv", saida)

    def test_global_intercepto_em_funcao_com_carregar_pesos(self):
        """Função que faz intercepto = valor escalar emite global intercepto (scalar)."""
        args = [
            LiteralNode(kind="cadeia", value="modelo.txt"),
        ]
        call = CallExprNode(
            callee=LiteralNode(kind="ident", value="carregar_pesos"),
            args=args,
        )
        assign = AssignNode(
            alvo=LiteralNode(kind="ident", value="intercepto"),
            valor=call,
        )

        funcao = FunctionNode(
            nome="restaurar_modelo",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[assign]),
        )

        inicio = FunctionNode(
            nome="inicio",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[]),
        )

        global_intercepto = VarDeclNode(
            tipo=TypeNode(base="real", is_array=False),
            nome="intercepto",
        )

        programa = ProgramNode(
            funcoes=[funcao, inicio],
            globais=[global_intercepto],
            dialeto="portugol_studio",
        )

        saida = self.emissor.gerar(programa)

        self.assertIn("global intercepto", saida)
        self.assertIn('intercepto = carregar_pesos("modelo.txt")', saida)
        self.assertIn("from runtime_portugol import carregar_pesos", saida)


if __name__ == "__main__":
    unittest.main()
