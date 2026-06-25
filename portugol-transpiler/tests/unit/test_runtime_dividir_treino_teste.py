"""Tests for dividir_treino_teste (in-place shuffle + train count)."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from runtime_portugol import dividir_treino_teste


class TestDividirTreinoTeste(unittest.TestCase):
    """Contrato in-place: embaralha X/y e devolve o tamanho do treino."""

    def test_retorna_tamanho_treino_80_20(self):
        """FR-009: 100 amostras com frac_teste=0.2 -> 80 de treino."""
        X = [[float(i), float(i + 1)] for i in range(100)]
        y = [float(i) for i in range(100)]
        n_tr = dividir_treino_teste(X, y, frac_teste=0.2, semente=42)
        self.assertEqual(n_tr, 80)
        self.assertEqual(len(X), 100)
        self.assertEqual(len(y), 100)

    def test_embaralha_in_place(self):
        """A lista X/y é reordenada in-place (mesmo objeto, nova ordem)."""
        X = [[float(i)] for i in range(10)]
        y = [float(i) for i in range(10)]
        id_X, id_y = id(X), id(y)
        dividir_treino_teste(X, y, frac_teste=0.2, semente=42)
        self.assertEqual(id(X), id_X)
        self.assertEqual(id(y), id_y)
        self.assertNotEqual([row[0] for row in X], list(range(10)))

    def test_determinismo_mesma_semente(self):
        """SC-003: mesma semente produz a mesma permutação."""
        X1 = [[float(i)] for i in range(50)]
        y1 = [float(i) for i in range(50)]
        X2 = [[float(i)] for i in range(50)]
        y2 = [float(i) for i in range(50)]
        dividir_treino_teste(X1, y1, frac_teste=0.2, semente=42)
        dividir_treino_teste(X2, y2, frac_teste=0.2, semente=42)
        self.assertEqual(X1, X2)
        self.assertEqual(y1, y2)

    def test_pareamento_x_y_preservado(self):
        """FR-011: o pareamento X[i] <-> y[i] é preservado após embaralhar."""
        X = [[float(i), float(i * 10)] for i in range(50)]
        y = [float(i) for i in range(50)]
        dividir_treino_teste(X, y, frac_teste=0.2, semente=42)
        for i in range(50):
            self.assertEqual(X[i][0], y[i])

    def test_sem_perda_de_amostras(self):
        """Nenhuma amostra é perdida: o conjunto continua o mesmo, só reordenado."""
        X = [[float(i)] for i in range(30)]
        y = [float(i) for i in range(30)]
        dividir_treino_teste(X, y, frac_teste=0.3, semente=7)
        self.assertEqual(sorted(v for v in y), [float(i) for i in range(30)])


if __name__ == "__main__":
    unittest.main()
