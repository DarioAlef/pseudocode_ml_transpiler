"""Tests for dividir_treino_teste function (User Story 3)."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from runtime_portugol import dividir_treino_teste


class TestDividirTreinoTeste(unittest.TestCase):
    """Test dividir_treino_teste function."""

    def test_determinismo_mesma_semente(self):
        """SC-003: Same seed produces identical partition in two calls."""
        X = [[float(i), float(i+1)] for i in range(100)]
        y = [float(i % 2) for i in range(100)]

        X1, X2 = [row[:] for row in X], [row[:] for row in X]
        y1 = y[:]
        y2 = y[:]

        Xtr1, ytr1, Xte1, yte1 = dividir_treino_teste(X1, y1, frac_teste=0.2, semente=42)
        Xtr2, ytr2, Xte2, yte2 = dividir_treino_teste(X2, y2, frac_teste=0.2, semente=42)

        self.assertEqual(Xtr1, Xtr2)
        self.assertEqual(ytr1, ytr2)
        self.assertEqual(Xte1, Xte2)
        self.assertEqual(yte1, yte2)

    def test_proporcao_80_20(self):
        """FR-009: 80/20 proportion for 100 samples with frac_teste=0.2."""
        X = [[float(i), float(i+1)] for i in range(100)]
        y = [float(i % 2) for i in range(100)]

        Xtr, ytr, Xte, yte = dividir_treino_teste(X, y, frac_teste=0.2, semente=42)

        self.assertEqual(len(ytr), 80)
        self.assertEqual(len(yte), 20)
        self.assertEqual(len(Xtr), 80)
        self.assertEqual(len(Xte), 20)

    def test_pareamento_x_y_preservado(self):
        """FR-011: X↔y pairing preserved within each subset."""
        X = [[float(i), float(i*10)] for i in range(50)]
        y = [float(i) for i in range(50)]

        Xtr, ytr, Xte, yte = dividir_treino_teste(X, y, frac_teste=0.2, semente=42)

        for i in range(len(ytr)):
            x_val = Xtr[i][0]
            y_val = ytr[i]
            self.assertEqual(x_val, y_val, f"Pairing mismatch in train set at index {i}")

        for i in range(len(yte)):
            x_val = Xte[i][0]
            y_val = yte[i]
            self.assertEqual(x_val, y_val, f"Pairing mismatch in test set at index {i}")

    def test_ordem_retorno_correta(self):
        """SC-003: Return order is (Xtr, ytr, Xte, yte)."""
        X = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0], [9.0, 10.0]]
        y = [1.0, 2.0, 3.0, 4.0, 5.0]

        result = dividir_treino_teste(X, y, frac_teste=0.2, semente=42)
        self.assertEqual(len(result), 4)

        Xtr, ytr, Xte, yte = result

        self.assertIsInstance(Xtr, list)
        self.assertIsInstance(ytr, list)
        self.assertIsInstance(Xte, list)
        self.assertIsInstance(yte, list)

        self.assertTrue(all(isinstance(row, list) for row in Xtr), "Xtr should be list of lists")
        self.assertTrue(all(isinstance(v, (int, float)) for v in ytr), "ytr should be list of floats")
        self.assertTrue(all(isinstance(row, list) for row in Xte), "Xte should be list of lists")
        self.assertTrue(all(isinstance(v, (int, float)) for v in yte), "yte should be list of floats")

    def test_total_amostras_preservado(self):
        """FR-011: len(Xtr) + len(Xte) == len(y)."""
        X = [[float(i), float(i+1)] for i in range(100)]
        y = [float(i % 2) for i in range(100)]

        Xtr, ytr, Xte, yte = dividir_treino_teste(X, y, frac_teste=0.2, semente=42)

        total = len(Xtr) + len(Xte)
        self.assertEqual(total, len(y))
        self.assertEqual(len(ytr) + len(yte), len(y))


if __name__ == "__main__":
    unittest.main()
