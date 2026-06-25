"""Tests for normalizar_zscore function (User Story 2)."""

import sys
import os
import math
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from runtime_portugol import normalizar_zscore


class TestNormalizarZScore(unittest.TestCase):
    """Test normalizar_zscore function."""

    def test_normalizacao_media_desvio(self):
        """SC-002: After normalization, each column has |mean| ≤ 1e-9 and |stdev-1| ≤ 1e-9."""
        X = [
            [1.0, 10.0, 100.0],
            [2.0, 20.0, 200.0],
            [3.0, 30.0, 300.0],
            [4.0, 40.0, 400.0],
            [5.0, 50.0, 500.0],
        ]
        n, f = 5, 3
        medias, desvios = normalizar_zscore(X, n, f)

        self.assertEqual(len(medias), 3)
        self.assertEqual(len(desvios), 3)

        for j in range(f):
            col_values = [X[i][j] for i in range(n)]
            col_mean = sum(col_values) / n
            col_var = sum((v - col_mean) ** 2 for v in col_values) / n
            col_stdev = math.sqrt(col_var)

            self.assertLess(abs(col_mean), 1e-9, f"Column {j} mean not ~0: {col_mean}")
            self.assertLess(abs(col_stdev - 1.0), 1e-9, f"Column {j} stdev not ~1: {col_stdev}")

    def test_coluna_constante_sem_divisao_por_zero(self):
        """FR-007: Constant column (stdev=0) treated as 1.0 without division by zero."""
        X = [
            [1.0, 5.0],
            [2.0, 5.0],
            [3.0, 5.0],
        ]
        n, f = 3, 2
        medias, desvios = normalizar_zscore(X, n, f)

        self.assertEqual(desvios[1], 1.0, "Constant column desvio should be 1.0")
        self.assertTrue(all(math.isfinite(x) for row in X for x in row), "All values should be finite")

    def test_n_zero_ou_f_zero(self):
        """FR-008: n==0 or f==0 returns ([], []) without modifying X."""
        X = [[1.0, 2.0], [3.0, 4.0]]
        X_copy = [row[:] for row in X]

        medias, desvios = normalizar_zscore(X, 0, 2)
        self.assertEqual(medias, [])
        self.assertEqual(desvios, [])
        self.assertEqual(X, X_copy, "X should not be modified when n==0")

        X = [[1.0, 2.0], [3.0, 4.0]]
        X_copy = [row[:] for row in X]
        medias, desvios = normalizar_zscore(X, 2, 0)
        self.assertEqual(medias, [])
        self.assertEqual(desvios, [])
        self.assertEqual(X, X_copy, "X should not be modified when f==0")

    def test_modificacao_inplace(self):
        """FR-007: Modification is in-place (same reference)."""
        X = [
            [1.0, 10.0],
            [2.0, 20.0],
            [3.0, 30.0],
        ]
        X_id = id(X)
        n, f = 3, 2
        medias, desvios = normalizar_zscore(X, n, f)

        self.assertEqual(id(X), X_id, "X reference should be the same (in-place modification)")
        for j in range(f):
            col_mean = sum(X[i][j] for i in range(n)) / n
            self.assertLess(abs(col_mean), 1e-9, f"Column {j} should have mean ~0")


if __name__ == "__main__":
    unittest.main()
