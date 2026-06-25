"""Contrato da API pública do parser (T002, FR-001/FR-020).

Cobre: importação dos símbolos Parser, parse, ErroSintatico; assinatura
básica; invariante de não criar novos tipos de nó.
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize  # noqa: E402
from ast_nodes import ProgramNode  # noqa: E402

CODIGO_MEDIA = """programa {
  funcao inicio() {
    real nota_1
    real nota_2
    real media
    escreva("oi")
    leia(nota_1)
    media = (nota_1 + nota_2) / 2
  }
}"""


class C_ImportTest(unittest.TestCase):
    def test_importa_Parser(self):
        from parser import Parser  # noqa: F401

    def test_importa_parse(self):
        from parser import parse  # noqa: F401

    def test_importa_ErroSintatico(self):
        from parser import ErroSintatico  # noqa: F401


class C_ErroSintaticoTest(unittest.TestCase):
    def setUp(self):
        from parser import ErroSintatico
        self.ErroSintatico = ErroSintatico

    def test_e_exception(self):
        self.assertTrue(issubclass(self.ErroSintatico, Exception))

    def test_atributos(self):
        e = self.ErroSintatico(3, 7, "esperado }")
        self.assertEqual(e.linha, 3)
        self.assertEqual(e.coluna, 7)
        self.assertEqual(e.mensagem, "esperado }")

    def test_str_formato(self):
        e = self.ErroSintatico(3, 7, "esperado }")
        s = str(e)
        self.assertIn("3", s)
        self.assertIn("7", s)
        self.assertIn("sintatico", s.lower())


class C_ParserApiTest(unittest.TestCase):
    def setUp(self):
        from parser import Parser, parse, ErroSintatico
        self.Parser = Parser
        self.parse = parse
        self.ErroSintatico = ErroSintatico

    def test_Parser_aceita_lista_tokens(self):
        tokens = tokenize(CODIGO_MEDIA)
        p = self.Parser(tokens)
        self.assertIsNotNone(p)

    def test_parse_retorna_ProgramNode(self):
        tokens = tokenize(CODIGO_MEDIA)
        ast = self.Parser(tokens).parse()
        self.assertIsInstance(ast, ProgramNode)

    def test_funcao_conveniencia_equivalente(self):
        tokens = tokenize(CODIGO_MEDIA)
        ast = self.parse(tokens)
        self.assertIsInstance(ast, ProgramNode)

    def test_dialeto_portugol_studio(self):
        tokens = tokenize(CODIGO_MEDIA)
        ast = self.Parser(tokens).parse()
        self.assertEqual(ast.dialeto, "portugol_studio")

    def test_erro_com_linha_coluna(self):
        tokens = tokenize("programa { funcao inicio( }")
        with self.assertRaises(self.ErroSintatico) as ctx:
            self.Parser(tokens).parse()
        e = ctx.exception
        self.assertIsInstance(e.linha, int)
        self.assertIsInstance(e.coluna, int)
        self.assertGreaterEqual(e.linha, 1)
        self.assertGreaterEqual(e.coluna, 1)

    def test_determinismo(self):
        tokens1 = tokenize(CODIGO_MEDIA)
        tokens2 = tokenize(CODIGO_MEDIA)
        ast1 = self.Parser(tokens1).parse()
        ast2 = self.Parser(tokens2).parse()
        self.assertEqual(ast1, ast2)


if __name__ == "__main__":
    unittest.main()
