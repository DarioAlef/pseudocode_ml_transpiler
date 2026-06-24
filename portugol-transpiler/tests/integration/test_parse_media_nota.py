"""Teste de integracao: parsear 01_media_nota.por ponta-a-ponta (T008, US1).

Cobre SC-001 (ProgramNode + funcao inicio + 3 VarDeclNode) e
SC-002 (divisao aplicada a soma parentetizada).
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from parser import Parser  # noqa: E402
from ast_nodes import (  # noqa: E402
    AssignNode,
    BinaryExprNode,
    FunctionNode,
    LiteralNode,
    ProgramNode,
    VarDeclNode,
)

EXERCISES_DIR = os.path.abspath(
    os.path.join(PROJECT_DIR, "..", "exercises_portugol")
)
CAMINHO_MEDIA = os.path.join(EXERCISES_DIR, "01_media_nota.por")


def _ast_media():
    with open(CAMINHO_MEDIA, encoding="utf-8") as f:
        codigo = f.read()
    return Parser(tokenize(codigo)).parse()


class SC001ProgramaEstrutura(unittest.TestCase):
    def test_parse_sem_excecao(self):
        ast = _ast_media()
        self.assertIsNotNone(ast)

    def test_retorna_ProgramNode(self):
        ast = _ast_media()
        self.assertIsInstance(ast, ProgramNode)

    def test_dialeto(self):
        ast = _ast_media()
        self.assertEqual(ast.dialeto, "portugol_studio")

    def test_funcao_inicio_presente(self):
        ast = _ast_media()
        nomes = [f.nome for f in ast.funcoes]
        self.assertIn("inicio", nomes)

    def test_funcao_inicio_e_FunctionNode(self):
        ast = _ast_media()
        inicio = next(f for f in ast.funcoes if f.nome == "inicio")
        self.assertIsInstance(inicio, FunctionNode)
        self.assertIsNone(inicio.tipo_retorno)

    def test_tres_declaracoes_de_variavel(self):
        ast = _ast_media()
        inicio = next(f for f in ast.funcoes if f.nome == "inicio")
        decls = [s for s in inicio.body.stmts if isinstance(s, VarDeclNode)]
        self.assertEqual(len(decls), 3)

    def test_nomes_variaveis(self):
        ast = _ast_media()
        inicio = next(f for f in ast.funcoes if f.nome == "inicio")
        decls = [s for s in inicio.body.stmts if isinstance(s, VarDeclNode)]
        nomes = {d.nome for d in decls}
        self.assertEqual(nomes, {"nota_1", "nota_2", "media"})

    def test_tipos_variaveis_real(self):
        ast = _ast_media()
        inicio = next(f for f in ast.funcoes if f.nome == "inicio")
        decls = [s for s in inicio.body.stmts if isinstance(s, VarDeclNode)]
        for d in decls:
            self.assertEqual(d.tipo.base, "real")


class SC002PrecedenciaExpressao(unittest.TestCase):
    def _assign_media(self):
        ast = _ast_media()
        inicio = next(f for f in ast.funcoes if f.nome == "inicio")
        assigns = [s for s in inicio.body.stmts if isinstance(s, AssignNode)]
        media_assign = next(
            a for a in assigns
            if isinstance(a.alvo, LiteralNode) and a.alvo.value == "media"
        )
        return media_assign

    def test_atribuicao_media_presente(self):
        self._assign_media()

    def test_valor_e_divisao(self):
        assign = self._assign_media()
        self.assertIsInstance(assign.valor, BinaryExprNode)
        self.assertEqual(assign.valor.op, "/")

    def test_numerador_e_soma(self):
        assign = self._assign_media()
        self.assertIsInstance(assign.valor.left, BinaryExprNode)
        self.assertEqual(assign.valor.left.op, "+")

    def test_denominador_e_literal_2(self):
        assign = self._assign_media()
        denominador = assign.valor.right
        self.assertIsInstance(denominador, LiteralNode)
        self.assertEqual(denominador.value, "2")


if __name__ == "__main__":
    unittest.main()
