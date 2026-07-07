"""Gera um dataset de treino maior e realista a partir dos dados reais.

Os 10 registros reais (Recre.io/dados_vendas.txt -> dados_cantina.csv) sao poucos
para treinar um modelo. Em vez de interpolacao SMOTE (que aqui era degenerada e
vazava o alvo), simulamos varios dias de operacao com um MODELO DE DEMANDA
coerente com o dominio de uma cantina escolar:

    demanda = demanda_base[produto]                    # media do item nos dados reais
              + bonus_dia[dia_semana]                   # movimento por dia (aditivo)
              - ELASTICIDADE * demanda_base * var_preco # preco sobe -> vende menos
              + ruido_gaussiano

O efeito de dia e ADITIVO (nao multiplicativo) para manter a relacao aproximadamente
linear -- adequada a demonstrar regressao linear. Ha um SINAL real (preco e dia)
para o modelo recuperar, com ruido realista, sem vazamento e sem balanceamento
artificial de classe (o alvo agora e continuo: quantidade vendida).

Entrada:  Recre.io/dados_cantina.csv  (base real gerada por preparar_dados.py)
Saida:    Recre.io/dados_cantina.csv  (base real + linhas sinteticas, embaralhado)
"""

import csv
import random
from statistics import mean

CAMINHO = "Recre.io/dados_cantina.csv"          # legivel (produto_id)
CAMINHO_TREINO = "Recre.io/dados_treino.csv"    # codificado p/ o modelo (one-hot)
NUM_TOTAL_DESEJADO = 240
ELASTICIDADE = 0.9          # sensibilidade da demanda ao preco
RUIDO_REL = 0.06            # desvio do ruido como fracao da demanda base
SEMENTE = 42

# Movimento tipico de uma cantina escolar (efeito ADITIVO, em unidades vendidas):
# dias uteis cheios, fim de semana fraco. Aditivo mantem a relacao ~linear.
BONUS_DIA = {
    1: 8,     # Segunda
    2: 5,     # Terca
    3: 5,     # Quarta
    4: 6,     # Quinta
    5: 12,    # Sexta (movimento alto)
    6: -18,   # Sabado (escola parcial)
    7: -35,   # Domingo (praticamente fechado)
}
# Dias com peso de amostragem (poucos registros no fim de semana).
DIAS_PESOS = {1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 2, 7: 1}


def carregar_base(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        leitor = csv.reader(f)
        cabecalho = next(leitor)
        linhas = []
        for linha in leitor:
            if not linha:
                continue
            linhas.append([
                int(float(linha[0])),   # produto_id
                int(float(linha[1])),   # dia_semana
                float(linha[2]),        # preco_item
                float(linha[3]),        # qtd_vendida
            ])
    return cabecalho, linhas


def perfil_produtos(linhas):
    """Estima preco base e demanda base por produto a partir dos dados reais."""
    perfis = {}
    ids = sorted({l[0] for l in linhas})
    for pid in ids:
        registros = [l for l in linhas if l[0] == pid]
        preco_base = mean(r[2] for r in registros)
        demanda_base = mean(r[3] for r in registros)
        perfis[pid] = {"preco_base": preco_base, "demanda_base": demanda_base}
    return perfis


def gerar_linha(pid, perfil, rng):
    preco_base = perfil["preco_base"]
    demanda_base = perfil["demanda_base"]

    dias = list(DIAS_PESOS.keys())
    pesos = list(DIAS_PESOS.values())
    dia = rng.choices(dias, weights=pesos, k=1)[0]

    # Preco varia em torno do base (promocoes/reajustes).
    preco = preco_base * rng.uniform(0.85, 1.15)
    var_preco = (preco - preco_base) / preco_base

    demanda = demanda_base + BONUS_DIA[dia] - ELASTICIDADE * demanda_base * var_preco
    demanda += rng.gauss(0.0, demanda_base * RUIDO_REL)
    demanda = max(0.0, round(demanda))

    return [pid, dia, round(preco, 2), demanda]


def aumentar(linhas, num_total, rng):
    perfis = perfil_produtos(linhas)
    ids = sorted(perfis.keys())
    resultado = list(linhas)
    while len(resultado) < num_total:
        pid = rng.choice(ids)
        resultado.append(gerar_linha(pid, perfis[pid], rng))
    rng.shuffle(resultado)
    return resultado


def winsorizar(linhas, pct=0.98):
    """Limita picos extremos de demanda ao percentil `pct` (winsorizacao).

    Alguns registros reais tem demanda muito acima do que qualquer feature
    explica (ex.: uma sexta atipica). Como o modelo nao tem como prever esses
    picos, eles so distorcem a avaliacao e o grafico. Limitamos o alvo ao teto do
    percentil para o dataset de treino. O arquivo bruto (dados_vendas.txt) NAO e
    alterado. Retorna o teto aplicado.
    """
    vendas = sorted(l[3] for l in linhas)
    if not vendas:
        return 0.0
    k = min(len(vendas) - 1, int(len(vendas) * pct))
    teto = vendas[k]
    for l in linhas:
        if l[3] > teto:
            l[3] = teto
    return teto


def salvar(cabecalho, linhas, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabecalho)
        for l in linhas:
            escritor.writerow([l[0], l[1], round(l[2], 2), l[3]])


def salvar_treino_onehot(linhas, caminho):
    """Escreve o CSV de treino com produto_id codificado em one-hot.

    produto_id (categorico) vira N colunas 0/1 (produto_1..produto_N). Isso
    permite a regressao linear aprender um intercepto por produto, em vez de
    tratar o id como um numero ordinal (o que nao faz sentido). Colunas finais:
        produto_1..produto_N, dia_semana, preco_item, qtd_vendida
    Retorna a lista de ids (para o mapa de colunas).
    """
    ids = sorted({l[0] for l in linhas})
    cabecalho = [f"produto_{pid}" for pid in ids] + [
        "dia_semana", "preco_item", "qtd_vendida"
    ]
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(cabecalho)
        for l in linhas:
            dummies = [1 if l[0] == pid else 0 for pid in ids]
            escritor.writerow(dummies + [l[1], round(l[2], 2), l[3]])
    return ids


if __name__ == "__main__":
    rng = random.Random(SEMENTE)
    cabecalho, base = carregar_base(CAMINHO)
    dados = aumentar(base, NUM_TOTAL_DESEJADO, rng)
    teto = winsorizar(dados)
    salvar(cabecalho, dados, CAMINHO)
    ids = salvar_treino_onehot(dados, CAMINHO_TREINO)
    print(f"Winsorizacao: demanda limitada a {teto:.0f} (picos atipicos aparados)")

    vendas = [l[3] for l in dados]
    print(f"Dataset gerado: {len(dados)} registros (reais: {len(base)})")
    print(f"  legivel  -> {CAMINHO}")
    print(f"  treino   -> {CAMINHO_TREINO}  (one-hot: {len(ids)} produtos)")
    print(f"  NUM_FEATURES para o .por = {len(ids) + 2}  (produtos + dia_semana + preco_item)")
    print(f"qtd_vendida  min={min(vendas):.0f}  media={mean(vendas):.1f}  max={max(vendas):.0f}")
