"""Runtime isolado de E/S e suporte a ML do transpilador Portugol -> Python.

Responsabilidade: oferecer as primitivas de entrada/saida (leitura de CSV,
escrita de resultados) e funcoes de apoio a aprendizado de maquina
(normalizacao, etc.) usadas pelos programas transpilados.
"""

import csv
import math
import random

# Estatisticas da ultima normalizacao de treino, guardadas para que o grafico de
# recomendacao possa padronizar novos cenarios ("amanha") do mesmo jeito que o
# modelo foi treinado.
_NORM_MEDIAS = None
_NORM_DESVIOS = None


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
    global _NORM_MEDIAS, _NORM_DESVIOS
    _NORM_MEDIAS = medias
    _NORM_DESVIOS = desvios
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


def plotar_previsoes(caminho, y_real, y_prev, inicio, fim, r2=None, rmse=None,
                     titulo="Previsao de demanda: Real vs Previsto (teste)"):
    """Gera um grafico SVG (sem dependencias externas) comparando real x previsto.

    Recorta as amostras de teste [inicio:fim), ordena pelo valor real (leitura
    mais clara) e desenha duas series: o valor REAL medido (azul) e o valor
    PREVISTO pelo modelo (laranja). Quanto mais as curvas se sobrepoem, melhor a
    previsao. O SVG e texto puro: abre em qualquer navegador. Devolve o caminho.
    """
    reais = list(y_real[inicio:fim])
    prev = list(y_prev[inicio:fim])
    n = len(reais)
    if n == 0:
        return caminho

    ordem = sorted(range(n), key=lambda k: reais[k])
    reais = [reais[k] for k in ordem]
    prev = [prev[k] for k in ordem]

    W, H = 820, 500
    ml, mr, mt, mb = 70, 30, 60, 60
    pw, ph = W - ml - mr, H - mt - mb

    vmin = min(min(reais), min(prev))
    vmax = max(max(reais), max(prev))
    if vmax == vmin:
        vmax = vmin + 1.0
    folga = (vmax - vmin) * 0.05
    vmin -= folga
    vmax += folga

    def px(i):
        return ml + pw / 2 if n == 1 else ml + pw * i / (n - 1)

    def py(v):
        return mt + ph * (1 - (v - vmin) / (vmax - vmin))

    def polyline(vals, cor):
        pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(vals))
        return f'<polyline fill="none" stroke="{cor}" stroke-width="2" points="{pts}"/>'

    def pontos(vals, cor):
        return "".join(
            f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="3" fill="{cor}"/>'
            for i, v in enumerate(vals)
        )

    azul, laranja = "#2563eb", "#f97316"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="sans-serif">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="28" font-size="18" font-weight="bold" '
         f'text-anchor="middle" fill="#111">{titulo}</text>',
         f'<text x="{W/2}" y="46" font-size="12" text-anchor="middle" '
         f'fill="#666">Azul = venda real; laranja = previsao do modelo. '
         f'Quanto mais as curvas se sobrepoem, melhor a previsao.</text>']

    for t in range(6):
        v = vmin + (vmax - vmin) * t / 5
        yy = py(v)
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml + pw}" y2="{yy:.1f}" '
                 f'stroke="#e6e6e6" stroke-width="1"/>')
        s.append(f'<text x="{ml - 8}" y="{yy + 4:.1f}" font-size="12" '
                 f'text-anchor="end" fill="#555">{v:.0f}</text>')

    s.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + ph}" '
             f'stroke="#333" stroke-width="1.5"/>')
    s.append(f'<line x1="{ml}" y1="{mt + ph}" x2="{ml + pw}" y2="{mt + ph}" '
             f'stroke="#333" stroke-width="1.5"/>')

    s.append(polyline(reais, azul))
    s.append(pontos(reais, azul))
    s.append(polyline(prev, laranja))
    s.append(pontos(prev, laranja))

    s.append(f'<text x="{ml + pw / 2}" y="{H - 18}" font-size="13" '
             f'text-anchor="middle" fill="#333">'
             f'Amostras de teste (ordenadas pela venda real)</text>')
    cy = mt + ph / 2
    s.append(f'<text x="18" y="{cy:.0f}" font-size="13" text-anchor="middle" '
             f'fill="#333" transform="rotate(-90 18 {cy:.0f})">'
             f'Quantidade vendida</text>')

    lx, ly = ml + 15, mt + 12
    s.append(f'<rect x="{lx - 8}" y="{ly - 14}" width="180" height="48" '
             f'fill="white" stroke="#ccc"/>')
    s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 22}" y2="{ly}" '
             f'stroke="{azul}" stroke-width="3"/>'
             f'<circle cx="{lx + 11}" cy="{ly}" r="3" fill="{azul}"/>')
    s.append(f'<text x="{lx + 30}" y="{ly + 4}" font-size="12" '
             f'fill="#333">Real (dados)</text>')
    s.append(f'<line x1="{lx}" y1="{ly + 20}" x2="{lx + 22}" y2="{ly + 20}" '
             f'stroke="{laranja}" stroke-width="3"/>'
             f'<circle cx="{lx + 11}" cy="{ly + 20}" r="3" fill="{laranja}"/>')
    s.append(f'<text x="{lx + 30}" y="{ly + 24}" font-size="12" '
             f'fill="#333">Previsto (modelo)</text>')

    s.append('</svg>')

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    return caminho


def plotar_dispersao(caminho, y_real, y_prev, inicio, fim, r2=None, rmse=None,
                     titulo="Ajuste do modelo: Previsto x Real (teste)"):
    """Grafico de dispersao (SVG): cada ponto de teste = (real, previsto).

    A linha tracejada e o "previsto = real" (acerto perfeito). Pontos acima dela
    o modelo superestimou; abaixo, subestimou. Nuvem colada a linha = bom ajuste.
    Este formato nao distorce os extremos como o grafico de linha ordenado.
    """
    reais = list(y_real[inicio:fim])
    prev = list(y_prev[inicio:fim])
    n = len(reais)
    if n == 0:
        return caminho

    W, H = 640, 620
    ml, mr, mt, mb = 75, 30, 72, 72
    pw, ph = W - ml - mr, H - mt - mb
    lo = min(min(reais), min(prev))
    hi = max(max(reais), max(prev))
    if hi == lo:
        hi = lo + 1.0
    folga = (hi - lo) * 0.05
    lo -= folga
    hi += folga

    def sx(v):
        return ml + pw * (v - lo) / (hi - lo)

    def sy(v):
        return mt + ph * (1 - (v - lo) / (hi - lo))

    azul = "#2563eb"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="sans-serif">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="30" font-size="17" font-weight="bold" '
         f'text-anchor="middle" fill="#111">{titulo}</text>',
         f'<text x="{W/2}" y="50" font-size="12" text-anchor="middle" '
         f'fill="#666">Cada ponto = uma amostra de teste. Tracejado = previsao '
         f'perfeita.</text>']

    for t in range(6):
        v = lo + (hi - lo) * t / 5
        yy = sy(v)
        xx = sx(v)
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+pw}" y2="{yy:.1f}" '
                 f'stroke="#eee" stroke-width="1"/>')
        s.append(f'<text x="{ml-8}" y="{yy+4:.1f}" font-size="11" '
                 f'text-anchor="end" fill="#555">{v:.0f}</text>')
        s.append(f'<text x="{xx:.1f}" y="{mt+ph+18:.1f}" font-size="11" '
                 f'text-anchor="middle" fill="#555">{v:.0f}</text>')

    s.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ph}" '
             f'stroke="#333" stroke-width="1.5"/>')
    s.append(f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" '
             f'stroke="#333" stroke-width="1.5"/>')
    s.append(f'<line x1="{sx(lo):.1f}" y1="{sy(lo):.1f}" x2="{sx(hi):.1f}" '
             f'y2="{sy(hi):.1f}" stroke="#f97316" stroke-width="2" '
             f'stroke-dasharray="6 4"/>')

    for r_, p_ in zip(reais, prev):
        s.append(f'<circle cx="{sx(r_):.1f}" cy="{sy(p_):.1f}" r="4" '
                 f'fill="{azul}" fill-opacity="0.55"/>')

    s.append(f'<text x="{ml+pw/2}" y="{H-22}" font-size="13" '
             f'text-anchor="middle" fill="#333">Venda real (unidades)</text>')
    cy = mt + ph / 2
    s.append(f'<text x="20" y="{cy:.0f}" font-size="13" text-anchor="middle" '
             f'fill="#333" transform="rotate(-90 20 {cy:.0f})">'
             f'Venda prevista (unidades)</text>')
    s.append(f'<line x1="{ml+15}" y1="{mt+15}" x2="{ml+45}" y2="{mt+15}" '
             f'stroke="#f97316" stroke-width="2" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{ml+52}" y="{mt+19}" font-size="12" fill="#333">'
             f'previsto = real (ideal)</text>')
    if r2 is not None and rmse is not None:
        s.append(f'<text x="{ml+15}" y="{mt+38}" font-size="12" fill="#111">'
                 f'R2 = {r2:.2f}   RMSE = {rmse:.1f} unidades</text>')
    s.append('</svg>')

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    return caminho


_DIAS_NOME = {1: "Segunda-feira", 2: "Terca-feira", 3: "Quarta-feira",
              4: "Quinta-feira", 5: "Sexta-feira", 6: "Sabado", 7: "Domingo"}


def recomendar_producao(caminho_csv, caminho_svg, pesos, intercepto, dia_alvo,
                        caminho_legenda=""):
    """Usa o modelo treinado para recomendar quanto produzir por produto num dia.

    Le o CSV de treino (colunas one-hot produto_1..N, dia_semana, preco_item,
    qtd_vendida), estima o preco tipico de cada produto e monta o cenario do dia
    `dia_alvo` (ex.: amanha). Aplica os pesos do modelo (padronizando com as
    estatisticas guardadas por normalizar_treino_teste) e desenha um grafico de
    barras SVG com a quantidade sugerida de producao/compra por produto.
    """
    with open(caminho_csv, newline="", encoding="utf-8") as f:
        linhas = [l for l in csv.reader(f) if l]
    cabecalho = linhas[0]
    dados = [[float(v) for v in l] for l in linhas[1:]]
    total_col = len(cabecalho)
    n_prod = total_col - 3           # produtos one-hot + dia_semana + preco + alvo
    idx_preco = n_prod + 1
    f_feat = total_col - 1

    nomes = {}
    if caminho_legenda:
        try:
            with open(caminho_legenda, newline="", encoding="utf-8") as f:
                for l in csv.reader(f):
                    if not l or l[0].strip().lower() in ("id", ""):
                        continue
                    nomes[int(float(l[0]))] = l[1]
        except OSError:
            pass

    precos = []
    for p in range(n_prod):
        vals = [d[idx_preco] for d in dados if d[p] == 1]
        precos.append(sum(vals) / len(vals) if vals else 0.0)

    medias = _NORM_MEDIAS
    desvios = _NORM_DESVIOS
    if medias is None or desvios is None:
        medias = [sum(d[j] for d in dados) / len(dados) for j in range(f_feat)]
        desvios = []
        for j in range(f_feat):
            var = sum((d[j] - medias[j]) ** 2 for d in dados) / len(dados)
            desvios.append(math.sqrt(var) or 1.0)

    demandas = []
    for p in range(n_prod):
        vec = [1.0 if j == p else 0.0 for j in range(n_prod)]
        vec.append(float(dia_alvo))
        vec.append(precos[p])
        z = [(vec[j] - medias[j]) / desvios[j] for j in range(f_feat)]
        pred = intercepto + sum(pesos[j] * z[j] for j in range(f_feat))
        demandas.append(max(0.0, pred))

    rotulos = [nomes.get(p + 1, f"Produto {p + 1}") for p in range(n_prod)]
    dia_nome = _DIAS_NOME.get(int(dia_alvo), f"dia {int(dia_alvo)}")

    W, H = 880, 540
    ml, mr, mt, mb = 75, 30, 82, 120
    pw, ph = W - ml - mr, H - mt - mb
    vmax = (max(demandas) if demandas else 1.0) * 1.2 or 1.0

    def by(v):
        return mt + ph * (1 - v / vmax)

    laranja = "#f97316"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'font-family="sans-serif">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         f'<text x="{W/2}" y="34" font-size="19" font-weight="bold" '
         f'text-anchor="middle" fill="#111">Recomendacao de producao para '
         f'{dia_nome}</text>',
         f'<text x="{W/2}" y="56" font-size="13" text-anchor="middle" '
         f'fill="#555">Quantas unidades produzir/comprar de cada produto, '
         f'segundo o modelo</text>']

    for t in range(6):
        v = vmax * t / 5
        yy = by(v)
        s.append(f'<line x1="{ml}" y1="{yy:.1f}" x2="{ml+pw}" y2="{yy:.1f}" '
                 f'stroke="#eee" stroke-width="1"/>')
        s.append(f'<text x="{ml-8}" y="{yy+4:.1f}" font-size="11" '
                 f'text-anchor="end" fill="#555">{v:.0f}</text>')

    s.append(f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt+ph}" '
             f'stroke="#333" stroke-width="1.5"/>')
    s.append(f'<line x1="{ml}" y1="{mt+ph}" x2="{ml+pw}" y2="{mt+ph}" '
             f'stroke="#333" stroke-width="1.5"/>')

    passo = pw / n_prod
    larg = passo * 0.6
    for p in range(n_prod):
        cx = ml + passo * (p + 0.5)
        x0 = cx - larg / 2
        v = demandas[p]
        y0 = by(v)
        s.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{larg:.1f}" '
                 f'height="{mt+ph-y0:.1f}" fill="{laranja}" rx="3"/>')
        s.append(f'<text x="{cx:.1f}" y="{y0-6:.1f}" font-size="14" '
                 f'font-weight="bold" text-anchor="middle" fill="#111">'
                 f'{v:.0f}</text>')
        s.append(f'<text x="{cx:.1f}" y="{mt+ph+16:.1f}" font-size="11" '
                 f'text-anchor="end" fill="#333" '
                 f'transform="rotate(-25 {cx:.1f} {mt+ph+16:.1f})">'
                 f'{rotulos[p]} (R${precos[p]:.2f})</text>')

    s.append(f'<text x="22" y="{mt+ph/2:.0f}" font-size="13" '
             f'text-anchor="middle" fill="#333" '
             f'transform="rotate(-90 22 {mt+ph/2:.0f})">'
             f'Unidades a produzir</text>')
    s.append('</svg>')

    with open(caminho_svg, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    return caminho_svg


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
