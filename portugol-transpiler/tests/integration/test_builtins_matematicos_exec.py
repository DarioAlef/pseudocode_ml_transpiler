"""Testes de integracao: transpila programas Portugol com builtins matematicos e executa (T005, T010, US1, US3).

Cobre:
  - Transpilar e executar programa com funcoes essenciais (raiz, potencia, logaritmo, exp, absoluto) (SC-001, SC-002)
  - Transpilar e executar programa com funcoes adicionais (seno, cosseno, piso, teto, arredondar, minimo, maximo) (SC-003)
  - Transpilar e executar aleatorio() (SC-003)
  - Verificar resultados esperados
"""

import os
import sys
import unittest
import tempfile
import subprocess
import math

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import tokenize, ErroLexico  # noqa: E402
from parser import parse, ErroSintatico  # noqa: E402
from emissor import emitir  # noqa: E402


def _transpilar_e_executar(codigo_portugol):
    """Transpila codigo Portugol e executa o resultado; retorna output e returncode."""
    try:
        tokens = tokenize(codigo_portugol)
        ast = parse(tokens)
        codigo_python = emitir(ast)
    except (ErroLexico, ErroSintatico, Exception) as e:
        raise RuntimeError(f"Erro ao transpilar: {e}")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(codigo_python)
        f.flush()
        temp_file = f.name

    try:
        resultado = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return resultado.stdout, resultado.stderr, resultado.returncode
    finally:
        os.unlink(temp_file)


class ExecutacaoEssenciaisTest(unittest.TestCase):
    """Testes de execucao das funcoes essenciais (US1)."""

    def test_raiz_16_retorna_4_0(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(raiz(16))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("4.0", stdout)

    def test_exp_0_retorna_1_0(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(exp(0))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("1.0", stdout)

    def test_potencia_2_3_retorna_8_0(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(potencia(2, 3))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("8.0", stdout)

    def test_absoluto_5_negativo_retorna_5(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(absoluto(-5))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("5", stdout)

    def test_logaritmo_1_retorna_0_0(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(logaritmo(1))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("0.0", stdout)


class ExecutacaoAdicionaisTest(unittest.TestCase):
    """Testes de execucao das funcoes adicionais (US3)."""

    def test_seno_0_retorna_0_0(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(seno(0))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("0.0", stdout)

    def test_cosseno_0_retorna_1_0(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(cosseno(0))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("1.0", stdout)

    def test_piso_2_7_retorna_2(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(piso(2.7))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("2", stdout)

    def test_teto_2_1_retorna_3(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(teto(2.1))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("3", stdout)

    def test_arredondar_2_5_retorna_2_ou_3(self):
        """Python 3 usa "round half to even" (banker's rounding); 2.5 -> 2."""
        codigo = """
programa {
  funcao inicio() {
    escreval(arredondar(2.5))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("2", stdout)

    def test_minimo_3_7_retorna_3(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(minimo(3, 7))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("3", stdout)

    def test_maximo_3_7_retorna_7(self):
        codigo = """
programa {
  funcao inicio() {
    escreval(maximo(3, 7))
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        self.assertIn("7", stdout)


class ExecutacaoAleatórioTest(unittest.TestCase):
    """Testes de execucao de aleatorio() (US3, SC-003)."""

    def test_aleatorio_retorna_valor_entre_0_e_1(self):
        """Executa aleatorio() e verifica que o resultado é um numero entre 0 e 1."""
        codigo = """
programa {
  funcao inicio() {
    escreval(aleatorio())
  }
}
"""
        stdout, stderr, returncode = _transpilar_e_executar(codigo)
        self.assertEqual(returncode, 0, f"stderr: {stderr}")
        try:
            valor = float(stdout.strip())
            self.assertGreaterEqual(valor, 0.0)
            self.assertLess(valor, 1.0)
        except ValueError:
            self.fail(f"aleatorio() nao retornou um numero: {stdout}")


if __name__ == "__main__":
    unittest.main()
