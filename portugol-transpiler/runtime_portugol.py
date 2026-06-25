"""Runtime isolado de E/S e suporte a ML do transpilador Portugol -> Python.

Responsabilidade: oferecer as primitivas de entrada/saida (leitura de CSV,
escrita de resultados) e funcoes de apoio a aprendizado de maquina
(normalizacao, etc.) usadas pelos programas transpilados.
"""

import csv
import math
import random


def ler_csv(caminho, X, y, sep=",", pular_cabecalho=True):
    """Colhe as features e o rotulo da ultima coluna de um CSV.

    Preenche X (lista de listas) e y (lista). Limpa X e y antes de preencher.
    Filtra linhas vazias ou comentários (iniciando com #). Retorna o numero
    de linhas lidas (n real).
    """
    X.clear()
    y.clear()
    with open(caminho, newline="", encoding="utf-8") as f:
        leitor = csv.reader(f, delimiter=sep)
        linhas = list(leitor)

    linhas_filtradas = []
    for linha in linhas:
        if not linha or not linha[0] or linha[0].strip().startswith("#"):
            continue
        linhas_filtradas.append(linha)

    if pular_cabecalho and linhas_filtradas:
        linhas_filtradas = linhas_filtradas[1:]
    for linha in linhas_filtradas:
        valores = [float(v) for v in linha]
        X.append(valores[:-1])
        y.append(float(valores[-1]))
    return len(y)


def normalizar_zscore(X, n, f):
    """Padroniza (z-score) cada coluna de X[0:n][0:f] in-place.

    Recebe n e f explicitamente. Evita divisao por zero caso o desvio seja 0.
    Retorna (medias, desvios).
    """
    if n == 0 or f == 0:
        return [], []
    medias = [sum(X[i][j] for i in range(n)) / n for j in range(f)]
    desvios = []
    for j in range(f):
        var = sum((X[i][j] - medias[j]) ** 2 for i in range(n)) / n
        desvio_std = math.sqrt(var)
        if desvio_std == 0.0:
            desvio_std = 1.0
        desvios.append(desvio_std)
    for i in range(n):
        for j in range(f):
            X[i][j] = (X[i][j] - medias[j]) / desvios[j]
    return medias, desvios


def dividir_treino_teste(X, y, frac_teste=0.2, semente=42):
    """Divide X e y em treino/teste de forma deterministica com base em semente."""
    random.seed(semente)
    idx = list(range(len(y)))
    random.shuffle(idx)
    corte = int(len(y) * (1 - frac_teste))
    tr, te = idx[:corte], idx[corte:]
    return (
        [X[i] for i in tr],
        [y[i] for i in tr],
        [X[i] for i in te],
        [y[i] for i in te],
    )


def salvar_pesos(caminho, pesos, intercepto):
    """Grava os pesos (na primeira linha separados por espaco) e intercepto na saida."""
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(" ".join(str(p) for p in pesos) + "\n")
        f.write(str(intercepto) + "\n")


def carregar_pesos(caminho):
    """Carrega pesos e intercepto de um arquivo salvo por salvar_pesos.

    Linha 1: pesos separados por espaço. Linha 2: intercepto.
    Retorna (pesos, intercepto) tuple.
    """
    with open(caminho, "r", encoding="utf-8") as f:
        linha1 = f.readline().strip()
        linha2 = f.readline().strip()

    pesos = [float(t) for t in linha1.split()] if linha1 else []
    intercepto = float(linha2)
    return pesos, intercepto
