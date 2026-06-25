"""Testes unitarios de statements do emissor (T020, US2).

Cobre: se/elif/else (FR-008), enquanto (FR-009), para -> range (FR-010),
VarDeclNode vetor -> [z]*N (FR-005) e matriz -> [[z]*C for _ in range(L)]
(FR-006), atribuicao indexada.
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
    ForStmtNode,
    FunctionNode,
    IfStmtNode,
    IndexExprNode,
    LiteralNode,
    ProgramNode,
    TypeNode,
    VarDeclNode,
    WhileStmtNode,
)
from emissor import emitir  # noqa: E402


def _tipo(base, is_array=False, dims=None):
    return TypeNode(base=base, is_array=is_array, dims=dims)


def _programa_com(stmts):
    inicio = FunctionNode(nome="inicio", tipo_retorno=None, params=[],
                          body=BlockNode(stmts=stmts))
    return ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")


class SeSenaoTest(unittest.TestCase):
    def test_se_simples(self):
        prog = _programa_com([
            IfStmtNode(
                cond=LiteralNode(kind="logico", value="verdadeiro"),
                then=BlockNode(stmts=[
                    VarDeclNode(tipo=_tipo("inteiro"), nome="x")
                ]),
                elifs=[],
                else_=None,
            ),
        ])
        py = emitir(prog)
        self.assertIn("if True:", py)
        self.assertIn("x = 0", py)

    def test_se_elif_else(self):
        prog = _programa_com([
            IfStmtNode(
                cond=LiteralNode(kind="ident", value="a"),
                then=BlockNode(stmts=[]),
                elifs=[
                    (LiteralNode(kind="ident", value="b"),
                     BlockNode(stmts=[])),
                ],
                else_=BlockNode(stmts=[]),
            ),
        ])
        py = emitir(prog)
        self.assertIn("if a:", py)
        self.assertIn("elif b:", py)
        self.assertIn("else:", py)

    def test_blocos_vazios_emitem_pass(self):
        prog = _programa_com([
            IfStmtNode(
                cond=LiteralNode(kind="logico", value="verdadeiro"),
                then=BlockNode(stmts=[]),
                elifs=[],
                else_=BlockNode(stmts=[]),
            ),
        ])
        py = emitir(prog)
        self.assertIn("pass", py)
        compile(py, "<t>", "exec")


class EnquantoTest(unittest.TestCase):
    def test_enquanto_simples(self):
        prog = _programa_com([
            WhileStmtNode(
                cond=LiteralNode(kind="ident", value="x"),
                body=BlockNode(stmts=[
                    AssignNode(
                        alvo=LiteralNode(kind="ident", value="x"),
                        valor=LiteralNode(kind="int", value="1"),
                    ),
                ]),
            ),
        ])
        py = emitir(prog)
        self.assertIn("while x:", py)
        self.assertIn("x = 1", py)


class ParaRangeTest(unittest.TestCase):
    def _para_padrao(self, op="<", post_op="+", post_val="1"):
        init = VarDeclNode(
            tipo=_tipo("inteiro"),
            nome="i",
            init=LiteralNode(kind="int", value="0"),
        )
        cond = BinaryExprNode(
            op=op,
            left=LiteralNode(kind="ident", value="i"),
            right=LiteralNode(kind="int", value="10"),
        )
        post = AssignNode(
            alvo=LiteralNode(kind="ident", value="i"),
            valor=BinaryExprNode(
                op=post_op,
                left=LiteralNode(kind="ident", value="i"),
                right=LiteralNode(kind="int", value=post_val),
            ),
        )
        return ForStmtNode(init=init, cond=cond, post=post,
                            body=BlockNode(stmts=[]))

    def test_para_padrao_vira_range(self):
        prog = _programa_com([self._para_padrao()])
        py = emitir(prog)
        self.assertIn("for i in range(0, 10):", py)

    def test_para_com_le_vira_range_com_mais_1(self):
        prog = _programa_com([self._para_padrao(op="<=")])
        py = emitir(prog)
        self.assertIn("range(0, 10 + 1)", py)

    def test_para_corpo_vazio_emite_pass(self):
        prog = _programa_com([self._para_padrao()])
        py = emitir(prog)
        self.assertIn("pass", py)
        compile(py, "<t>", "exec")


class VetorMatrizTest(unittest.TestCase):
    def test_vetor_emite_lista_zero_vezes_N(self):
        prog = _programa_com([
            VarDeclNode(
                tipo=_tipo("inteiro", is_array=True,
                            dims=[LiteralNode(kind="int", value="5")]),
                nome="v",
            ),
        ])
        py = emitir(prog)
        self.assertIn("v = [0] * 5", py)

    def test_matriz_emite_lista_aninhada(self):
        prog = _programa_com([
            VarDeclNode(
                tipo=_tipo("real", is_array=True,
                            dims=[LiteralNode(kind="int", value="3"),
                                   LiteralNode(kind="int", value="4")]),
                nome="m",
            ),
        ])
        py = emitir(prog)
        self.assertIn("[[0.0] * 4 for _ in range(3)]", py)

    def test_vetor_real_zero_0_ponto_0(self):
        prog = _programa_com([
            VarDeclNode(
                tipo=_tipo("real", is_array=True,
                            dims=[LiteralNode(kind="int", value="2")]),
                nome="vr",
            ),
        ])
        py = emitir(prog)
        self.assertIn("[0.0] * 2", py)


class AtribuicaoIndexadaTest(unittest.TestCase):
    def test_atribuicao_vetor_indice(self):
        prog = _programa_com([
            AssignNode(
                alvo=IndexExprNode(
                    base=LiteralNode(kind="ident", value="v"),
                    indices=[LiteralNode(kind="int", value="0")],
                ),
                valor=LiteralNode(kind="int", value="42"),
            ),
        ])
        py = emitir(prog)
        self.assertIn("v[0] = 42", py)

    def test_atribuicao_matriz_dois_indices(self):
        prog = _programa_com([
            AssignNode(
                alvo=IndexExprNode(
                    base=LiteralNode(kind="ident", value="m"),
                    indices=[LiteralNode(kind="int", value="1"),
                              LiteralNode(kind="int", value="2")],
                ),
                valor=LiteralNode(kind="real", value="3.5"),
            ),
        ])
        py = emitir(prog)
        self.assertIn("m[1][2] = 3.5", py)


if __name__ == "__main__":
    unittest.main()
