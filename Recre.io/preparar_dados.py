"""Extrai os dados reais de vendas para o formato de treino do modelo.

Objetivo do projeto (Recre.io): prever a DEMANDA (quantidade vendida) de cada
item para recomendar quanto produzir no dia seguinte -- reduzindo desperdicio.
Por isso o alvo (ultima coluna) e `qtd_vendida`, um valor continuo, adequado a
REGRESSAO LINEAR.

Features (todas conhecidas ANTES de produzir, sem vazamento de alvo):
    produto_id   -- identidade do item (1..N)
    dia_semana   -- 1=Segunda ... 7=Domingo
    preco_item   -- preco de venda unitario

Entrada:  Recre.io/dados_vendas.txt
    Data;DiaSemana;Produto;QtdProduzida;QtdVendida;Faturamento;Sobras
Saida:    Recre.io/dados_cantina.csv  (produto_id,dia_semana,preco_item,qtd_vendida)
"""

import csv

CAMINHO_VENDAS = "Recre.io/dados_vendas.txt"
CAMINHO_SAIDA = "Recre.io/dados_cantina.csv"
CAMINHO_LEGENDA = "Recre.io/produtos_legenda.csv"

DIAS_SEMANA = {
    "Segunda-feira": 1,
    "Terca-feira": 2,
    "Terça-feira": 2,
    "Quarta-feira": 3,
    "Quinta-feira": 4,
    "Sexta-feira": 5,
    "Sabado": 6,
    "Sábado": 6,
    "Domingo": 7,
}


def processar_vendas(caminho):
    """Le o log de vendas e devolve (linhas, mapa_produtos).

    linhas: lista de [produto_id, dia_semana, preco_item, qtd_vendida]
    mapa_produtos: {nome_produto: produto_id} na ordem de primeira aparicao.
    """
    linhas = []
    mapa_produtos = {}
    proximo_id = 1

    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("Data;"):
                continue
            partes = linha.split(";")
            if len(partes) < 6:
                continue

            dia_nome = partes[1]
            nome_produto = partes[2]
            qtd_produzida = float(partes[3])
            qtd_vendida = float(partes[4])
            faturamento = float(partes[5])

            dia = DIAS_SEMANA.get(dia_nome, 0)
            if dia == 0:
                continue

            # Preco unitario derivado do faturamento (nao depende de produtos.txt,
            # cujo join com os nomes esta desalinhado). Fallback para qtd_produzida.
            base = qtd_vendida if qtd_vendida > 0 else qtd_produzida
            preco = round(faturamento / base, 2) if base > 0 else 0.0

            if nome_produto not in mapa_produtos:
                mapa_produtos[nome_produto] = proximo_id
                proximo_id += 1
            produto_id = mapa_produtos[nome_produto]

            linhas.append([produto_id, float(dia), preco, qtd_vendida])

    return linhas, mapa_produtos


def salvar_csv(linhas, caminho):
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["produto_id", "dia_semana", "preco_item", "qtd_vendida"])
        escritor.writerows(linhas)


def salvar_legenda(mapa_produtos, caminho):
    """Grava id,nome de cada produto para rotular o grafico de recomendacao."""
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["id", "nome"])
        for nome, pid in mapa_produtos.items():
            escritor.writerow([pid, nome])


if __name__ == "__main__":
    linhas, mapa_produtos = processar_vendas(CAMINHO_VENDAS)
    salvar_csv(linhas, CAMINHO_SAIDA)
    salvar_legenda(mapa_produtos, CAMINHO_LEGENDA)
    print(f"Dados reais extraidos: {len(linhas)} registros -> {CAMINHO_SAIDA}")
    print(f"Legenda de produtos -> {CAMINHO_LEGENDA}")
    print("Mapa de produtos (nome -> id):")
    for nome, pid in mapa_produtos.items():
        print(f"  {pid}: {nome}")
