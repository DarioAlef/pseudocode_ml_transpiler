"""Testes unitarios dos nos da AST (ast_nodes.py).

Cobre SC-001 (instanciacao), SC-003 (__repr__), FR-002 (posicao),
FR-020 (sem efeitos colaterais), FR-022 (opcionais ausentes = None),
Acceptance Scenarios US1, US2, US3.
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
    ForStmtNode,
    FunctionNode,
    IfStmtNode,
    IndexExprNode,
    LiteralNode,
    Node,
    ParamNode,
    Position,
    ProgramNode,
    ReturnStmtNode,
    TypeNode,
    UnaryExprNode,
    VarDeclNode,
    WhileStmtNode,
)


class InstanciacaoBasicaTest(unittest.TestCase):
    """T004 — instanciacao de cada no com argumentos validos."""

    def test_position(self):
        p = Position(10, 5, "x.por")
        self.assertEqual(p.linha, 10)
        self.assertEqual(p.coluna, 5)
        self.assertEqual(p.arquivo, "x.por")

    def test_position_defaults(self):
        p = Position()
        self.assertEqual(p.linha, 0)
        self.assertEqual(p.coluna, 0)
        self.assertEqual(p.arquivo, "")

    def test_node_base(self):
        n = Node()
        self.assertIsNone(n.pos)

    def test_program_node(self):
        n = ProgramNode([], [])
        self.assertEqual(n.funcoes, [])
        self.assertEqual(n.globais, [])
        self.assertEqual(n.dialeto, "portugol_studio")

    def test_function_node(self):
        n = FunctionNode(nome="f", tipo_retorno=TypeNode("inteiro"), params=[], body=BlockNode([]))
        self.assertEqual(n.nome, "f")
        self.assertIsNotNone(n.tipo_retorno)
        self.assertEqual(n.body, BlockNode([]))

    def test_param_node(self):
        n = ParamNode(tipo=TypeNode("real"), nome="x", is_ref=True)
        self.assertEqual(n.nome, "x")
        self.assertTrue(n.is_ref)

    def test_var_decl_node(self):
        n = VarDeclNode(tipo=TypeNode("inteiro"), nome="i", init=LiteralNode("inteiro", 0))
        self.assertEqual(n.nome, "i")
        self.assertIsNotNone(n.init)

    def test_type_node_escalar(self):
        n = TypeNode(base="real")
        self.assertEqual(n.base, "real")
        self.assertFalse(n.is_array)
        self.assertIsNone(n.dims)

    def test_type_node_array(self):
        n = TypeNode(base="real", is_array=True, dims=[5000, 4])
        self.assertTrue(n.is_array)
        self.assertEqual(n.dims, [5000, 4])

    def test_block_node(self):
        stmt = AssignNode()
        n = BlockNode(stmts=[stmt])
        self.assertEqual(len(n.stmts), 1)

    def test_if_stmt_node(self):
        n = IfStmtNode(cond=LiteralNode("logico", True), then=BlockNode([]))
        self.assertIsNotNone(n.cond)
        self.assertIsNone(n.else_)

    def test_for_stmt_node(self):
        n = ForStmtNode(
            init=AssignNode(),
            cond=LiteralNode("logico", True),
            post=AssignNode(),
            body=BlockNode([]),
        )
        self.assertIsNotNone(n.init)
        self.assertIsNotNone(n.body)

    def test_while_stmt_node(self):
        n = WhileStmtNode(cond=LiteralNode("logico", True), body=BlockNode([]))
        self.assertIsNotNone(n.cond)
        self.assertIsNotNone(n.body)

    def test_assign_node(self):
        n = AssignNode(alvo=LiteralNode("inteiro", 0), op="=", valor=LiteralNode("inteiro", 1))
        self.assertEqual(n.op, "=")
        self.assertIsNotNone(n.alvo)

    def test_call_expr_node(self):
        n = CallExprNode(callee="f", args=[LiteralNode("inteiro", 1)])
        self.assertEqual(n.callee, "f")
        self.assertEqual(len(n.args), 1)

    def test_binary_expr_node(self):
        n = BinaryExprNode(op="+", left=LiteralNode("inteiro", 1), right=LiteralNode("inteiro", 2))
        self.assertEqual(n.op, "+")
        self.assertIsNotNone(n.left)

    def test_unary_expr_node(self):
        n = UnaryExprNode(op="-", operand=LiteralNode("inteiro", 5))
        self.assertEqual(n.op, "-")
        self.assertIsNotNone(n.operand)

    def test_literal_node(self):
        n = LiteralNode(kind="inteiro", value=42)
        self.assertEqual(n.kind, "inteiro")
        self.assertEqual(n.value, 42)

    def test_return_stmt_node(self):
        n = ReturnStmtNode(value=LiteralNode("inteiro", 0))
        self.assertIsNotNone(n.value)

    def test_index_expr_node(self):
        n = IndexExprNode(base=LiteralNode("inteiro", 0), indices=[LiteralNode("inteiro", 1)])
        self.assertIsNotNone(n.base)
        self.assertEqual(len(n.indices), 1)


class CasosDeBoraTest(unittest.TestCase):
    """T005 — casos de borda definidos na spec e FR-022."""

    def test_program_node_vazio(self):
        n = ProgramNode([], [])
        self.assertEqual(n.funcoes, [])
        self.assertEqual(n.globais, [])

    def test_block_node_vazio(self):
        n = BlockNode([])
        self.assertEqual(n.stmts, [])

    def test_call_expr_sem_args(self):
        n = CallExprNode("f", [])
        self.assertEqual(n.args, [])

    def test_function_node_sem_params(self):
        n = FunctionNode(nome="proc", tipo_retorno=None, params=[], body=None)
        self.assertIsNone(n.tipo_retorno)
        self.assertEqual(n.params, [])
        self.assertIsNone(n.body)

    def test_var_decl_sem_init(self):
        n = VarDeclNode(tipo=TypeNode("inteiro"), nome="x")
        self.assertIsNone(n.init)

    def test_return_stmt_sem_valor(self):
        n = ReturnStmtNode()
        self.assertIsNone(n.value)

    def test_type_node_escalar(self):
        n = TypeNode("real")
        self.assertFalse(n.is_array)
        self.assertIsNone(n.dims)

    def test_type_node_array_grande(self):
        n = TypeNode("real", is_array=True, dims=[5000, 4])
        self.assertEqual(n.dims, [5000, 4])

    def test_param_node_is_ref(self):
        n = ParamNode(is_ref=True)
        self.assertTrue(n.is_ref)

    def test_if_stmt_com_elifs_e_sem_else(self):
        cond2 = LiteralNode("logico", False)
        elif_block = BlockNode([])
        n = IfStmtNode(
            cond=LiteralNode("logico", True),
            then=BlockNode([]),
            elifs=[(cond2, elif_block)],
            else_=None,
        )
        self.assertEqual(len(n.elifs), 1)
        self.assertIsNone(n.else_)

    def test_if_stmt_com_else(self):
        n = IfStmtNode(
            cond=LiteralNode("logico", True),
            then=BlockNode([]),
            else_=BlockNode([ReturnStmtNode()]),
        )
        self.assertIsNotNone(n.else_)

    def test_index_expr_vetor_um_indice(self):
        n = IndexExprNode(base=LiteralNode("inteiro", 0), indices=[LiteralNode("inteiro", 1)])
        self.assertEqual(len(n.indices), 1)

    def test_index_expr_matriz_dois_indices(self):
        i = LiteralNode("inteiro", 0)
        j = LiteralNode("inteiro", 1)
        n = IndexExprNode(base=LiteralNode("inteiro", 0), indices=[i, j])
        self.assertEqual(len(n.indices), 2)

    def test_defaults_mutaveis_sao_independentes(self):
        b1 = BlockNode()
        b2 = BlockNode()
        b1.stmts.append(AssignNode())
        self.assertEqual(len(b2.stmts), 0)

    def test_call_args_mutaveis_sao_independentes(self):
        c1 = CallExprNode()
        c2 = CallExprNode()
        c1.args.append(LiteralNode("inteiro", 1))
        self.assertEqual(len(c2.args), 0)


class ArvorAninhadaTest(unittest.TestCase):
    """T006 — montagem de arvore aninhada e igualdade estrutural (Acceptance Scenario 3)."""

    def _build_tree(self):
        ret = ReturnStmtNode(value=LiteralNode("inteiro", 0))
        body = BlockNode(stmts=[ret])
        func = FunctionNode(
            nome="main",
            tipo_retorno=TypeNode("inteiro"),
            params=[],
            body=body,
        )
        return ProgramNode(funcoes=[func], globais=[])

    def test_montagem_e_acesso_em_profundidade(self):
        prog = self._build_tree()
        self.assertEqual(prog.funcoes[0].nome, "main")
        self.assertEqual(prog.funcoes[0].body.stmts[0].value.value, 0)

    def test_igualdade_estrutural(self):
        prog1 = self._build_tree()
        prog2 = self._build_tree()
        self.assertEqual(prog1, prog2)

    def test_desigualdade_estrutural(self):
        prog1 = self._build_tree()
        prog2 = ProgramNode(funcoes=[], globais=[])
        self.assertNotEqual(prog1, prog2)


class ReprTest(unittest.TestCase):
    """T013 — __repr__ legivel (US2, SC-003)."""

    def test_repr_contem_nome_da_classe(self):
        for no in [
            ProgramNode([], []),
            FunctionNode(),
            BlockNode([]),
            LiteralNode("inteiro", 42),
            ReturnStmtNode(),
            BinaryExprNode("+"),
        ]:
            nome = type(no).__name__
            with self.subTest(no=nome):
                self.assertIn(nome, repr(no))

    def test_repr_contem_campos(self):
        n = LiteralNode(kind="inteiro", value=42)
        r = repr(n)
        self.assertIn("kind", r)
        self.assertIn("value", r)
        self.assertIn("42", r)

    def test_repr_arvore_aninhada_contem_repr_filho(self):
        lit = LiteralNode("inteiro", 99)
        ret = ReturnStmtNode(value=lit)
        block = BlockNode(stmts=[ret])
        self.assertIn("LiteralNode", repr(block))
        self.assertIn("99", repr(block))

    def test_repr_program_node_vazio(self):
        r = repr(ProgramNode([], []))
        self.assertIn("ProgramNode", r)
        self.assertIn("funcoes", r)


class PosicaoTest(unittest.TestCase):
    """T016 — posicao de origem (US3, FR-002)."""

    def test_position_campos(self):
        p = Position(10, 5, "x.por")
        self.assertEqual(p.linha, 10)
        self.assertEqual(p.coluna, 5)
        self.assertEqual(p.arquivo, "x.por")

    def test_no_com_pos(self):
        pos = Position(3, 1, "prog.por")
        n = LiteralNode("inteiro", 1, pos=pos)
        self.assertEqual(n.pos, pos)

    def test_no_sem_pos_eh_none(self):
        n = LiteralNode("inteiro", 1)
        self.assertIsNone(n.pos)

    def test_pos_aceito_em_qualquer_no(self):
        pos = Position(1, 1, "a.por")
        nos = [
            ProgramNode([], [], pos=pos),
            FunctionNode(pos=pos),
            BlockNode(pos=pos),
            ReturnStmtNode(pos=pos),
        ]
        for no in nos:
            with self.subTest(no=type(no).__name__):
                self.assertEqual(no.pos, pos)


if __name__ == "__main__":
    unittest.main()
