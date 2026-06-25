"""Tests for salvar_pesos and carregar_pesos functions (User Story 4)."""

import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from runtime_portugol import salvar_pesos, carregar_pesos


class TestPesos(unittest.TestCase):
    """Test salvar_pesos and carregar_pesos functions."""

    def test_salvar_pesos_formato(self):
        """FR-013: salvar_pesos writes weights on line 1 and intercept on line 2."""
        pesos = [0.1, 0.2, 0.3]
        intercepto = 0.5

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            fname = f.name

        try:
            salvar_pesos(fname, pesos, intercepto)

            with open(fname, 'r', encoding='utf-8') as f:
                linhas = f.readlines()

            self.assertEqual(len(linhas), 2)
            self.assertEqual(linhas[0], "0.1 0.2 0.3\n")
            self.assertEqual(linhas[1], "0.5\n")
        finally:
            os.unlink(fname)

    def test_round_trip_exato(self):
        """SC-004: Round-trip salvar_pesos→carregar_pesos reproduces exact values (tolerance 1e-9)."""
        pesos = [0.123456789, 0.987654321, -0.5]
        intercepto = 0.75

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            fname = f.name

        try:
            salvar_pesos(fname, pesos, intercepto)
            pesos2, intercepto2 = carregar_pesos(fname)

            self.assertEqual(len(pesos2), len(pesos))
            for p1, p2 in zip(pesos, pesos2):
                self.assertLess(abs(p1 - p2), 1e-9)
            self.assertLess(abs(intercepto - intercepto2), 1e-9)
        finally:
            os.unlink(fname)

    def test_round_trip_pesos_vazios(self):
        """Edge case D2: Empty weights list handled correctly."""
        pesos = []
        intercepto = 0.42

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            fname = f.name

        try:
            salvar_pesos(fname, pesos, intercepto)

            with open(fname, 'r', encoding='utf-8') as f:
                linhas = f.readlines()

            self.assertEqual(len(linhas), 2)
            self.assertEqual(linhas[0], "\n")
            self.assertEqual(linhas[1], "0.42\n")

            pesos2, intercepto2 = carregar_pesos(fname)
            self.assertEqual(pesos2, [])
            self.assertLess(abs(intercepto - intercepto2), 1e-9)
        finally:
            os.unlink(fname)

    def test_carregar_pesos_retorno_tipo(self):
        """FR-015: carregar_pesos returns (list[float], float)."""
        pesos = [1.0, 2.0]
        intercepto = 3.0

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            fname = f.name

        try:
            salvar_pesos(fname, pesos, intercepto)
            pesos2, intercepto2 = carregar_pesos(fname)

            self.assertIsInstance(pesos2, list)
            self.assertIsInstance(intercepto2, float)
        finally:
            os.unlink(fname)

    def test_salvar_carregar_multiplos_pesos(self):
        """Test with larger weight vectors."""
        pesos = [0.1 * i for i in range(20)]
        intercepto = 0.99

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            fname = f.name

        try:
            salvar_pesos(fname, pesos, intercepto)
            pesos2, intercepto2 = carregar_pesos(fname)

            self.assertEqual(len(pesos2), 20)
            for p1, p2 in zip(pesos, pesos2):
                self.assertLess(abs(p1 - p2), 1e-9)
        finally:
            os.unlink(fname)


if __name__ == "__main__":
    unittest.main()
