"""Tests for normalizar_treino_teste (z-score com estatisticas do treino)."""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from runtime_portugol import normalizar_treino_teste


class TestNormalizarTreinoTeste(unittest.TestCase):
    """Padroniza usando medias/desvios do treino, aplicadas a treino + teste."""

    def test_treino_fica_com_media_zero(self):
        """As linhas de treino ficam com média ~0 por coluna."""
        X = [[0.0], [2.0], [4.0], [100.0]]
        n_tr = 3
        normalizar_treino_teste(X, n_tr, len(X), 1)
        media_treino = sum(X[i][0] for i in range(n_tr)) / n_tr
        self.assertAlmostEqual(media_treino, 0.0, places=9)

    def test_teste_usa_estatisticas_do_treino(self):
        """A linha de teste é padronizada com média/desvio do treino, não os seus."""
        X = [[0.0], [2.0], [4.0], [100.0]]
        n_tr = 3
        normalizar_treino_teste(X, n_tr, len(X), 1)
        media = (0.0 + 2.0 + 4.0) / 3
        var = ((0.0 - media) ** 2 + (2.0 - media) ** 2 + (4.0 - media) ** 2) / 3
        desvio = var ** 0.5
        esperado_teste = (100.0 - media) / desvio
        self.assertAlmostEqual(X[3][0], esperado_teste, places=9)

    def test_desvio_zero_nao_quebra(self):
        """Coluna constante no treino -> desvio tratado como 1.0 (sem divisão por zero)."""
        X = [[5.0], [5.0], [5.0], [9.0]]
        normalizar_treino_teste(X, 3, len(X), 1)
        self.assertEqual(X[0][0], 0.0)
        self.assertEqual(X[3][0], 4.0)

    def test_aplica_a_todas_as_linhas(self):
        """Todas as n_total linhas são modificadas in-place."""
        X = [[10.0, -2.0], [20.0, -4.0], [30.0, -6.0], [40.0, -8.0]]
        ret = normalizar_treino_teste(X, 2, 4, 2)
        self.assertEqual(ret, 4)
        for i in range(4):
            self.assertNotEqual(X[i][0], (10.0 + i * 10))


if __name__ == "__main__":
    unittest.main()
