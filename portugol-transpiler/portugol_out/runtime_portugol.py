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


def dividir_treino_teste(X, y, frac_teste=0.2, semente=None):
    """Embaralha X e y in-place (mesma permutacao) e devolve o tamanho do treino.

    Apos a chamada, as primeiras `n_treino` linhas de X/y sao o conjunto de
    treino e as restantes sao o conjunto de teste. A permutacao e deterministica
    pela `semente`. Segue o padrao in-place + retorno escalar de `ler_csv`, para
    ser consumivel pelo codigo Portugol transpilado (sem desempacotar tuplas).
    """
    n_total = len(y)
    random.seed(semente)
    idx = list(range(n_total))
    random.shuffle(idx)
    X[:] = [X[i] for i in idx]
    y[:] = [y[i] for i in idx]
    n_teste = int(n_total * frac_teste)
    return n_total - n_teste


def normalizar_treino_teste(X, n_tr, n_total, f):
    """Padroniza (z-score) X[0:n_total] in-place usando estatisticas do treino.

    As medias e desvios sao calculados apenas sobre as `n_tr` primeiras linhas
    (conjunto de treino) e aplicados a todas as `n_total` linhas (treino +
    teste). Isso evita vazamento de informacao do teste para o treino. Evita
    divisao por zero caso o desvio seja 0. Devolve `n_total`.
    """
    if n_tr == 0 or f == 0:
        return n_total
    medias = [sum(X[i][j] for i in range(n_tr)) / n_tr for j in range(f)]
    desvios = []
    for j in range(f):
        var = sum((X[i][j] - medias[j]) ** 2 for i in range(n_tr)) / n_tr
        desvio_std = math.sqrt(var)
        if desvio_std == 0.0:
            desvio_std = 1.0
        desvios.append(desvio_std)
    for i in range(n_total):
        for j in range(f):
            X[i][j] = (X[i][j] - medias[j]) / desvios[j]
    return n_total


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

import os

def limpa():
    """Limpa o terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


class arq:
    MODO_LEITURA = "r"
    MODO_ESCRITA = "w"
    MODO_ACRESCENTAR = "a"

    _arquivos = {}
    _next_fd = 1

    @classmethod
    def arquivo_existe(cls, caminho):
        return os.path.exists(caminho)

    @classmethod
    def abrir_arquivo(cls, caminho, modo):
        fd = cls._next_fd
        cls._next_fd += 1
        cls._arquivos[fd] = open(caminho, modo, encoding='utf-8')
        return fd

    @classmethod
    def ler_linha(cls, fd):
        if fd not in cls._arquivos:
            return ""
        return cls._arquivos[fd].readline().rstrip('\n')

    @classmethod
    def escrever_linha(cls, texto, fd):
        if fd in cls._arquivos:
            cls._arquivos[fd].write(texto)

    @classmethod
    def fim_arquivo(cls, fd):
        if fd not in cls._arquivos:
            return True
        f = cls._arquivos[fd]
        pos = f.tell()
        char = f.read(1)
        if not char:
            return True
        f.seek(pos)
        return False

    @classmethod
    def fechar_arquivo(cls, fd):
        if fd in cls._arquivos:
            cls._arquivos[fd].close()
            del cls._arquivos[fd]


class tx:
    @classmethod
    def posicao_texto(cls, sub, texto, inicio):
        try:
            return texto.index(sub, inicio)
        except ValueError:
            return -1

    @classmethod
    def extrair_subtexto(cls, texto, inicio, fim):
        return texto[inicio:fim]

    @classmethod
    def numero_caracteres(cls, texto):
        return len(texto)


class ti:
    @classmethod
    def cadeia_para_inteiro(cls, cadeia, base=10):
        try:
            return int(cadeia, base)
        except ValueError:
            return 0

    @classmethod
    def cadeia_para_real(cls, cadeia):
        try:
            return float(cadeia)
        except ValueError:
            return 0.0
