"""Testes unitarios de funcoes do emissor (T021, US2).

Cobre: def nome(params): + return (FR-011), procedimento sem return,
e injecao de `global N` quando funcao reatribui escalar global mas NAO para
listas mutadas nem variavel local homonima (FR-012).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from ast_nodes import (  # noqa: E402
    AssignNode,
    BinaryExprNode,
    BlockNode,
    FunctionNode,
    IndexExprNode,
    LiteralNode,
    ParamNode,
    ProgramNode,
    ReturnStmtNode,
    TypeNode,
    VarDeclNode,
)
from emissor import emitir  # noqa: E402


def _tipo(base, is_array=False, dims=None):
    return TypeNode(base=base, is_array=is_array, dims=dims)


class DefReturnTest(unittest.TestCase):
    def test_funcao_com_return(self):
        soma = FunctionNode(
            nome="soma",
            tipo_retorno=_tipo("inteiro"),
            params=[
                ParamNode(tipo=_tipo("inteiro"), nome="a"),
                ParamNode(tipo=_tipo("inteiro"), nome="b"),
            ],
            body=BlockNode(stmts=[
                ReturnStmtNode(value=BinaryExprNode(
                    op="+",
                    left=LiteralNode(kind="ident", value="a"),
                    right=LiteralNode(kind="ident", value="b"),
                )),
            ]),
        )
        prog = ProgramNode(funcoes=[soma], globais=[], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertIn("def soma(a, b):", py)
        self.assertIn("return (a + b)", py)

    def test_procedimento_sem_return(self):
        proc = FunctionNode(
            nome="ola",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[]),
        )
        prog = ProgramNode(funcoes=[proc], globais=[], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertIn("def ola():", py)
        self.assertIn("pass", py)
        compile(py, "<t>", "exec")

    def test_return_sem_valor(self):
        proc = FunctionNode(
            nome="proc",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[ReturnStmtNode(value=None)]),
        )
        prog = ProgramNode(funcoes=[proc], globais=[], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertIn("return", py)


class DiretivaGlobalTest(unittest.TestCase):
    def test_reatribuicao_escalar_global_injeta_global(self):
        global_x = VarDeclNode(tipo=_tipo("inteiro"), nome="x")
        func = FunctionNode(
            nome="modifica",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[
                AssignNode(
                    alvo=LiteralNode(kind="ident", value="x"),
                    valor=LiteralNode(kind="int", value="10"),
                ),
            ]),
        )
        prog = ProgramNode(funcoes=[func], globais=[global_x], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertIn("global x", py)

    def test_mutacao_lista_global_nao_injeta_global(self):
        global_v = VarDeclNode(
            tipo=_tipo("inteiro", is_array=True, dims=[LiteralNode(kind="int", value="5")]),
            nome="v",
        )
        func = FunctionNode(
            nome="modifica",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[
                AssignNode(
                    alvo=IndexExprNode(
                        base=LiteralNode(kind="ident", value="v"),
                        indices=[LiteralNode(kind="int", value="0")],
                    ),
                    valor=LiteralNode(kind="int", value="10"),
                ),
            ]),
        )
        prog = ProgramNode(funcoes=[func], globais=[global_v], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertNotIn("global v", py)

    def test_variavel_local_homonima_nao_injeta_global(self):
        global_x = VarDeclNode(tipo=_tipo("inteiro"), nome="x")
        func = FunctionNode(
            nome="modifica",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[
                VarDeclNode(tipo=_tipo("inteiro"), nome="x"),
                AssignNode(
                    alvo=LiteralNode(kind="ident", value="x"),
                    valor=LiteralNode(kind="int", value="10"),
                ),
            ]),
        )
        prog = ProgramNode(funcoes=[func], globais=[global_x], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertNotIn("global x", py)

    def test_parametro_nao_injeta_global(self):
        global_x = VarDeclNode(tipo=_tipo("inteiro"), nome="x")
        func = FunctionNode(
            nome="modifica",
            tipo_retorno=None,
            params=[ParamNode(tipo=_tipo("inteiro"), nome="x")],
            body=BlockNode(stmts=[
                AssignNode(
                    alvo=LiteralNode(kind="ident", value="x"),
                    valor=LiteralNode(kind="int", value="10"),
                ),
            ]),
        )
        prog = ProgramNode(funcoes=[func], globais=[global_x], dialeto="portugol_studio")
        py = emitir(prog)
        self.assertNotIn("global x", py)


if __name__ == "__main__":
    unittest.main()
