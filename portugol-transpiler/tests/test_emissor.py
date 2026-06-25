"""Testes ponta-a-ponta do emissor (Secao 11.2 da SPEC_DEFINITIVA).

Para cada `.por` de teste: transpila (.por -> .py), executa o .py gerado com
entrada fixa e compara o stdout com o valor esperado. Usa fixtures pytest para
transpilar e capturar a saida.
"""

import os
import subprocess
import sys

import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))


@pytest.fixture
def transpilar_e_rodar(tmp_path):
    """Devolve uma funcao que transpila um .por e roda o .py, capturando stdout."""

    def _executar(nome_por, entrada=None):
        caminho = os.path.join(TESTS_DIR, nome_por)
        out_dir = tmp_path / "out"
        transp = subprocess.run(
            [sys.executable, "transpilador.py", caminho, "--output-dir", str(out_dir)],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
        )
        assert transp.returncode == 0, transp.stderr
        nome_py = os.path.splitext(nome_por)[0] + ".py"
        gerado = out_dir / nome_py
        assert gerado.exists(), f"{gerado} nao foi gerado"
        execucao = subprocess.run(
            [sys.executable, str(gerado)],
            cwd=str(out_dir),
            capture_output=True,
            text=True,
            input=entrada,
        )
        assert execucao.returncode == 0, execucao.stderr
        return execucao.stdout

    return _executar


def test_media_de_dois_numeros(transpilar_e_rodar):
    saida = transpilar_e_rodar("media.por", entrada="7.0\n9.0\n")
    assert saida.strip() == "8.0"


def test_fatorial_iterativo(transpilar_e_rodar):
    saida = transpilar_e_rodar("fatorial.por", entrada="5\n")
    assert saida.strip() == "120"


def test_soma_de_vetor(transpilar_e_rodar):
    saida = transpilar_e_rodar("vetor.por")
    assert saida.strip() == "15"


@pytest.mark.parametrize(
    "n,esperado",
    [("0", "1"), ("1", "1"), ("4", "24"), ("6", "720")],
)
def test_fatorial_varios_valores(transpilar_e_rodar, n, esperado):
    saida = transpilar_e_rodar("fatorial.por", entrada=f"{n}\n")
    assert saida.strip() == esperado


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
