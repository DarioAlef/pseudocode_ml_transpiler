"""Testes unitarios do nucleo de expressoes do emissor (T010, US1/Foundational).

Cobre: literais (int/real/cadeia re-quotada/logico/ident), operadores
(^ -> **, logicos palavra e simbolo), parentetizacao/precedencia total,
indentacao de 4 espacos, e builtins de E/S.
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
    CallExprNode,
    FunctionNode,
    IfStmtNode,
    LiteralNode,
    ProgramNode,
    TypeNode,
    UnaryExprNode,
    VarDeclNode,
)
from emissor import emitir  # noqa: E402


def _emitir_programa_simples(stmts):
    """Monta ProgramNode com funcao inicio contendo stmts e emite codigo."""
    inicio = FunctionNode(nome="inicio", tipo_retorno=None, params=[],
                          body=BlockNode(stmts=stmts))
    prog = ProgramNode(funcoes=[inicio], globais=[], dialeto="portugol_studio")
    return emitir(prog)


class LiteralTest(unittest.TestCase):
    def test_int_emite_texto_cru(self):
        no = LiteralNode(kind="int", value="42")
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[AssignNode(alvo=LiteralNode(kind="ident", value="x"),
                                  valor=no)]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("42", py)

    def test_real_emite_texto_cru(self):
        no = LiteralNode(kind="real", value="0.5")
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[AssignNode(alvo=LiteralNode(kind="ident", value="x"),
                                  valor=no)]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("0.5", py)

    def test_cadeia_reinquota_com_aspas_duplas(self):
        no = LiteralNode(kind="cadeia", value="oi")
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[AssignNode(alvo=LiteralNode(kind="ident", value="x"),
                                  valor=no)]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("\"oi\"", py)

    def test_cadeia_com_aspa_interna_escapa(self):
        no = LiteralNode(kind="cadeia", value='disse "oi"')
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[AssignNode(alvo=LiteralNode(kind="ident", value="x"),
                                  valor=no)]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn(r'\"oi\"', py)

    def test_logico_verdadeiro_emite_True(self):
        no = LiteralNode(kind="logico", value="verdadeiro")
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[AssignNode(alvo=LiteralNode(kind="ident", value="x"),
                                  valor=no)]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("True", py)

    def test_logico_falso_emite_False(self):
        no = LiteralNode(kind="logico", value="falso")
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[AssignNode(alvo=LiteralNode(kind="ident", value="x"),
                                  valor=no)]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("False", py)

    def test_ident_emite_nome(self):
        no = LiteralNode(kind="ident", value="contador")
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[AssignNode(alvo=LiteralNode(kind="ident", value="x"),
                                  valor=no)]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("contador", py)


class OperadoresTest(unittest.TestCase):
    def _emitir_expr(self, expr):
        return _emitir_programa_simples([
            AssignNode(alvo=LiteralNode(kind="ident", value="r"), valor=expr)
        ])

    def test_potencia_vira_py_star_star(self):
        expr = BinaryExprNode(
            op="^",
            left=LiteralNode(kind="int", value="2"),
            right=LiteralNode(kind="int", value="3"),
        )
        py = self._emitir_expr(expr)
        self.assertIn("**", py)
        self.assertNotIn(" ^ ", py)

    def test_operador_logico_palavra_e_vira_and(self):
        expr = BinaryExprNode(
            op="e",
            left=LiteralNode(kind="logico", value="verdadeiro"),
            right=LiteralNode(kind="logico", value="falso"),
        )
        py = self._emitir_expr(expr)
        self.assertIn("and", py)

    def test_operador_logico_simbolo_andand_vira_and(self):
        expr = BinaryExprNode(
            op="&&",
            left=LiteralNode(kind="logico", value="verdadeiro"),
            right=LiteralNode(kind="logico", value="falso"),
        )
        py = self._emitir_expr(expr)
        self.assertIn("and", py)

    def test_operador_logico_palavra_ou_vira_or(self):
        expr = BinaryExprNode(
            op="ou",
            left=LiteralNode(kind="logico", value="verdadeiro"),
            right=LiteralNode(kind="logico", value="falso"),
        )
        py = self._emitir_expr(expr)
        self.assertIn("or", py)

    def test_operador_logico_simbolo_pipepipe_vira_or(self):
        expr = BinaryExprNode(
            op="||",
            left=LiteralNode(kind="logico", value="verdadeiro"),
            right=LiteralNode(kind="logico", value="falso"),
        )
        py = self._emitir_expr(expr)
        self.assertIn("or", py)

    def test_unario_nao_palavra_vira_not(self):
        expr = UnaryExprNode(op="nao", operand=LiteralNode(kind="logico", value="verdadeiro"))
        py = self._emitir_expr(expr)
        self.assertIn("not", py)

    def test_unario_exclamacao_vira_not(self):
        expr = UnaryExprNode(op="!", operand=LiteralNode(kind="logico", value="verdadeiro"))
        py = self._emitir_expr(expr)
        self.assertIn("not", py)


class ParentetizacaoTest(unittest.TestCase):
    def _emitir_expr(self, expr):
        return _emitir_programa_simples([
            AssignNode(alvo=LiteralNode(kind="ident", value="r"), valor=expr)
        ])

    def test_binario_envolvido_por_parenteses(self):
        expr = BinaryExprNode(
            op="+",
            left=LiteralNode(kind="int", value="1"),
            right=LiteralNode(kind="int", value="2"),
        )
        py = self._emitir_expr(expr)
        self.assertIn("(1 + 2)", py)

    def test_unario_envolvido_por_parenteses(self):
        expr = UnaryExprNode(op="-", operand=LiteralNode(kind="int", value="5"))
        py = self._emitir_expr(expr)
        self.assertIn("(- 5)", py)

    def test_precedencia_total_aninhada(self):
        expr = BinaryExprNode(
            op="+",
            left=BinaryExprNode(op="*",
                                left=LiteralNode(kind="int", value="2"),
                                right=LiteralNode(kind="int", value="3")),
            right=LiteralNode(kind="int", value="4"),
        )
        py = self._emitir_expr(expr)
        self.assertIn("((2 * 3) + 4)", py)


class IndentacaoTest(unittest.TestCase):
    def test_corpo_inicio_indentado_4_espacos(self):
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[VarDeclNode(tipo=_tipo("real"), nome="x")]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        linhas = py.splitlines()
        corpo = [ln for ln in linhas if "x = 0.0" in ln]
        self.assertTrue(corpo, "esperava linha de declaracao de x")
        self.assertTrue(corpo[0].startswith("    x = 0.0"))
        self.assertFalse(corpo[0].startswith("\t"))

    def test_nenhuma_tabulacao_no_gerado(self):
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[
                    IfStmtNode(
                        cond=LiteralNode(kind="logico", value="verdadeiro"),
                        then=BlockNode(stmts=[
                            VarDeclNode(tipo=_tipo("real"), nome="x")
                        ]),
                        elifs=[],
                        else_=None,
                    ),
                ]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        for ln in py.splitlines():
            self.assertNotIn("\t", ln)


def _tipo(base):
    return TypeNode(base=base, is_array=False, dims=None)


class BuiltinESTest(unittest.TestCase):
    def test_escreva_vira_print_sep_vazio_end_vazio(self):
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[CallExprNode(
                    callee=LiteralNode(kind="ident", value="escreva"),
                    args=[LiteralNode(kind="cadeia", value="oi")],
                )]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("print(\"oi\", sep=\"\", end=\"\")", py)

    def test_escreval_vira_print_padrao(self):
        prog = ProgramNode(
            funcoes=[FunctionNode(nome="inicio", body=BlockNode(
                stmts=[CallExprNode(
                    callee=LiteralNode(kind="ident", value="escreval"),
                    args=[LiteralNode(kind="cadeia", value="oi")],
                )]))],
            globais=[], dialeto="portugol_studio",
        )
        py = emitir(prog)
        self.assertIn("print(\"oi\")", py)
        self.assertNotIn("sep=\"\"", py)


if __name__ == "__main__":
    unittest.main()
