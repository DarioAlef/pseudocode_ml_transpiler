"""Gerador de dados sinteticos para o exemplo de regressao logistica (Card 15).

Produz um CSV linearmente separavel com 4 features aleatorias e um rotulo
binario, usando semente fixa para reprodutibilidade. O rotulo segue a funcao
geradora da Secao 11.1 da SPEC_DEFINITIVA.md:

    z = 2*x1 - 1*x2 + 0.5*x3 - 0.3*x4 + 0.5
    classe = 1 se z > 0, senao 0

Uso:
    python3 exemplos/gerar_dados.py [caminho_saida]

Sem `caminho_saida`, escreve em exemplos/dados_sinteticos.csv (ao lado deste
script). Apenas biblioteca padrao (csv, random). Nao modifica exemplos/dados.csv.
"""

import csv
import os
import random
import sys

CABECALHO = ["x1", "x2", "x3", "x4", "classe"]


def gerar(caminho, n=500, semente=42):
    """Escreve `n` linhas sinteticas em `caminho` (CSV com cabecalho).

    Usa `random.seed(semente)` antes de amostrar, garantindo saida
    deterministica. Cria o diretorio-pai se ausente. Devolve `n`.
    """
    pasta = os.path.dirname(os.path.abspath(caminho))
    os.makedirs(pasta, exist_ok=True)

    random.seed(semente)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(CABECALHO)
        for _ in range(n):
            x = [random.uniform(-3, 3) for _ in range(4)]
            z = 2.0 * x[0] - 1.0 * x[1] + 0.5 * x[2] - 0.3 * x[3] + 0.5
            rotulo = 1 if z > 0.0 else 0
            escritor.writerow([*x, rotulo])
    return n


def _caminho_padrao():
    """Devolve exemplos/dados_sinteticos.csv ao lado deste script."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_sinteticos.csv")


def main(argv=None):
    """Le o caminho de saida (opcional) dos argumentos e gera o CSV."""
    args = sys.argv[1:] if argv is None else argv
    caminho = args[0] if args else _caminho_padrao()
    n = gerar(caminho)
    print(f"Gerado: {caminho} ({n} linhas + cabecalho)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
