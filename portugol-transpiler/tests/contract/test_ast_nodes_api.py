"""Contrato da API publica do modulo ast_nodes.

Cobre FR-021 (import estrela expoe todas as classes), FR-001 (isinstance Node),
SC-002 (comando de aceite do card), T007 e T014.
"""

import os
import subprocess
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

_NOMES_CONTRATO = [
    "Position",
    "Node",
    "ProgramNode",
    "FunctionNode",
    "ParamNode",
    "VarDeclNode",
    "TypeNode",
    "BlockNode",
    "IfStmtNode",
    "ForStmtNode",
    "WhileStmtNode",
    "AssignNode",
    "CallExprNode",
    "BinaryExprNode",
    "UnaryExprNode",
    "LiteralNode",
    "ReturnStmtNode",
    "IndexExprNode",
]


class ImportEstrelaTest(unittest.TestCase):
    """T007 — from ast_nodes import * expoe os 18 nomes do contrato."""

    def setUp(self):
        import ast_nodes

        self._modulo = ast_nodes

    def test_todos_os_nomes_exportados(self):
        for nome in _NOMES_CONTRATO:
            with self.subTest(nome=nome):
                self.assertTrue(
                    hasattr(self._modulo, nome),
                    f"{nome} nao encontrado no modulo ast_nodes",
                )

    def test_nos_sao_instancia_de_node(self):
        from ast_nodes import Node

        nos_concretos = _NOMES_CONTRATO[2:]
        for nome in nos_concretos:
            with self.subTest(nome=nome):
                cls = getattr(self._modulo, nome)
                instancia = cls()
                self.assertIsInstance(
                    instancia,
                    Node,
                    f"{nome}() nao e isinstance de Node",
                )


class ComandoAceiteTest(unittest.TestCase):
    """T014 — comando de aceite do card via subprocess (SC-002)."""

    def test_aceite_exit_zero_e_contém_program_node(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from ast_nodes import *; print(ProgramNode([],[]))",
            ],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ProgramNode(", result.stdout)


if __name__ == "__main__":
    unittest.main()
