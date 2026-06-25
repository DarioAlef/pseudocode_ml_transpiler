"""Tests for ler_csv function (User Story 1)."""

import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from runtime_portugol import ler_csv


class TestLerCSV(unittest.TestCase):
    """Test ler_csv function with synthetic CSV data."""

    def test_ler_csv_500_linhas(self):
        """SC-001: CSV with 500 data lines returns 500."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("f1,f2,f3,label\n")
            for i in range(500):
                f.write(f"{i},1.0,2.0,{i % 2}\n")
            fname = f.name

        try:
            X, y = [], []
            n = ler_csv(fname, X, y)
            self.assertEqual(n, 500)
            self.assertEqual(len(X), 500)
            self.assertEqual(len(y), 500)
            self.assertEqual(len(X[0]), 3)
        finally:
            os.unlink(fname)

    def test_ler_csv_ultima_coluna_rotulo(self):
        """FR-003: Last column becomes label."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("f1,f2,f3,label\n")
            f.write("1.0,2.0,3.0,0.5\n")
            f.write("4.0,5.0,6.0,0.7\n")
            fname = f.name

        try:
            X, y = [], []
            ler_csv(fname, X, y)
            self.assertEqual(X[0], [1.0, 2.0, 3.0])
            self.assertEqual(X[1], [4.0, 5.0, 6.0])
            self.assertEqual(y[0], 0.5)
            self.assertEqual(y[1], 0.7)
        finally:
            os.unlink(fname)

    def test_ler_csv_separador_alternativo(self):
        """FR-004: Alternative separator (';') supported."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("f1;f2;f3;label\n")
            f.write("1.0;2.0;3.0;1.0\n")
            fname = f.name

        try:
            X, y = [], []
            ler_csv(fname, X, y, sep=";")
            self.assertEqual(X[0], [1.0, 2.0, 3.0])
            self.assertEqual(y[0], 1.0)
        finally:
            os.unlink(fname)

    def test_ler_csv_pular_cabecalho_false(self):
        """FR-004: pular_cabecalho=False treats all lines as data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("1,2,3,4\n")
            f.write("5,6,7,8\n")
            fname = f.name

        try:
            X, y = [], []
            n = ler_csv(fname, X, y, pular_cabecalho=False)
            self.assertEqual(n, 2)
            self.assertEqual(len(X), 2)
            self.assertEqual(X[0], [1.0, 2.0, 3.0])
        finally:
            os.unlink(fname)

    def test_ler_csv_linhas_vazias_ignoradas(self):
        """FR-005: Empty lines are ignored."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("f1,f2,label\n")
            f.write("1.0,2.0,0.5\n")
            f.write("\n")
            f.write("3.0,4.0,0.7\n")
            fname = f.name

        try:
            X, y = [], []
            n = ler_csv(fname, X, y)
            self.assertEqual(n, 2)
            self.assertEqual(len(X), 2)
        finally:
            os.unlink(fname)

    def test_ler_csv_comentarios_ignorados(self):
        """FR-005: Lines starting with '#' are ignored."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("f1,f2,label\n")
            f.write("1.0,2.0,0.5\n")
            f.write("# Comment line\n")
            f.write("3.0,4.0,0.7\n")
            fname = f.name

        try:
            X, y = [], []
            n = ler_csv(fname, X, y)
            self.assertEqual(n, 2)
            self.assertEqual(len(X), 2)
        finally:
            os.unlink(fname)

    def test_ler_csv_limpa_conteudo_previo(self):
        """FR-002: Previous content of X/y is cleared."""
        X = [[1.0, 2.0, 3.0]]
        y = [0.5]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("f1,f2,label\n")
            f.write("4.0,5.0,0.7\n")
            fname = f.name

        try:
            ler_csv(fname, X, y)
            self.assertEqual(len(X), 1)
            self.assertEqual(X[0], [4.0, 5.0])
            self.assertEqual(y[0], 0.7)
        finally:
            os.unlink(fname)


if __name__ == "__main__":
    unittest.main()
