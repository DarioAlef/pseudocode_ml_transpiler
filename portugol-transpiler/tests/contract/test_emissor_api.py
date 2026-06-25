"""Contrato da API publica do emissor (T011, US1, conforme contracts/emissor_api.md).

Cobre: emitir() retorna str; 1a linha == cabecalho; passa em compile();
determinismo (mesma entrada -> mesma saida); rodape com if __name__ == "__main__".
"""

import os
import sys
import unittest

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from emissor import Emissor, emitir  # noqa: E402
from lexer import tokenize  # noqa: E402
from parser import parse  # noqa: E402

CABECALHO = "# GERADO AUTOMATICAMENTE"

CODIGO_MEDIA = """programa {
  funcao inicio() {
    real nota_1
    real nota_2
    real media
    escreva("Digite a primeira nota:")
    leia(nota_1)
    escreva("Digite a segunda nota:")
    leia(nota_2)
    media = (nota_1 + nota_2) / 2
    escreva("A média da nota do aluno é: ", media)
  }
}"""


def _programa_media():
    return parse(tokenize(CODIGO_MEDIA))


class EmissorApiTest(unittest.TestCase):
    def test_emitir_retorna_str(self):
        py = emitir(_programa_media())
        self.assertIsInstance(py, str)

    def test_emitir_nao_vazio(self):
        py = emitir(_programa_media())
        self.assertGreater(len(py), 0)

    def test_primeira_linha_e_cabecalho(self):
        py = emitir(_programa_media())
        self.assertEqual(py.splitlines()[0], CABECALHO)

    def test_passa_em_compile(self):
        py = emitir(_programa_media())
        compile(py, "<gerado>", "exec")

    def test_determinismo_mesma_entrada_mesma_saida(self):
        py1 = emitir(_programa_media())
        py2 = emitir(_programa_media())
        self.assertEqual(py1, py2)

    def test_rodape_com_if_name_main(self):
        py = emitir(_programa_media())
        self.assertIn("if __name__ == \"__main__\":", py)
        self.assertIn("inicio()", py)

    def test_termina_com_newline(self):
        py = emitir(_programa_media())
        self.assertTrue(py.endswith("\n"))

    def test_classe_Emissor_gerar_equivalente_a_emitir(self):
        e = Emissor()
        py1 = e.gerar(_programa_media())
        py2 = emitir(_programa_media())
        self.assertEqual(py1, py2)

    def test_gerar_reinicia_estado_a_cada_chamada(self):
        e = Emissor()
        py1 = e.gerar(_programa_media())
        py2 = e.gerar(_programa_media())
        self.assertEqual(py1, py2)


if __name__ == "__main__":
    unittest.main()
