# Spec Definitiva — Transpilador Portugol → Python para Regressão Logística

> Objetivo final: **escrever e treinar uma regressão logística em Portugol, lendo
> dados de um arquivo CSV.** Este documento é a única spec do projeto — substituiu
> e apagou a versão anterior (Go + regressão *linear*), cujos erros estão
> catalogados na Seção 12.

---

## 0. Resumo das decisões (TL;DR)

1. **Alvo = Python, não Go.** Para o critério que você pediu ("o que for mais
   fácil"), Python é claramente o caminho mais simples. Justificativa na Seção 1.
2. **Algoritmo = regressão logística** (classificação), não linear. Muda a função
   de previsão (sigmoide), a função de custo (entropia cruzada / log-loss) e as
   métricas (acurácia, e não MSE/R²). Detalhes na Seção 4.
3. **Corte de escopo:** remova **toda** a parte de concorrência da spec antiga
   (`paralelo_para`, `goroutine`, `canal`, `mutex`, WaitGroup). É desnecessária
   para o objetivo e triplica a dificuldade. Veja Seção 2.
4. **Um único dialeto: Portugol Studio** (`programa { funcao inicio() }`, atribuição
   com `=`, índices a partir de 0). É o dialeto dos seus arquivos `01..06`. Esqueça
   o VisuAlg/Clássico (`algoritmo`, `<-`, `vetor[1..10]`) por enquanto.
5. A spec original (apagada) **tinha boa estrutura** (lexer → parser → AST →
   emissor), mas também **erros concretos que não compilariam**. Lista completa
   na Seção 12.

---

## 1. Pergunta 1 — Go ou Python? (resposta: Python)

A spec antiga argumenta "Go porque é rápido e a sintaxe é regular". Os dois
argumentos são verdadeiros, mas **respondem à pergunta errada**. Você não precisa
de velocidade de C para treinar uma regressão logística de aula, e "sintaxe regular
do alvo" não é o que torna um transpilador fácil de escrever. O que torna fácil é
**o quanto o alvo perdoa a imprecisão do código que você gera**.

| Critério (para o *seu* objetivo) | Go | Python | Vencedor |
|---|---|---|---|
| Tipagem do código gerado | Estática: todo `int64`/`float64` precisa ser explícito; conversões manuais. Erra fácil. | Dinâmica: o interpretador resolve tipos em runtime. Perdoa imprecisão do emissor. | **Python** |
| Imports/variáveis não usados | **Erro de compilação** em Go. Seu emissor vai quebrar o tempo todo. | Apenas avisos, nunca quebram. | **Python** |
| Ler CSV | Precisa de runtime próprio + `encoding/csv` + parse manual de float. | `csv`/`open` + `float()` na biblioteca padrão, trivial. | **Python** |
| Etapa de build | Gera `.go` → `go build` → binário. Mais um passo que pode falhar. | Gera `.py` → roda. | **Python** |
| Depurar a saída | Recompilar a cada tentativa. | Editar/rodar na hora; `print` em qualquer lugar. | **Python** |
| Indentação gerada | `gofmt` conserta tudo automaticamente. | Você precisa indentar certo (blocos por indentação). | **Go** |
| Velocidade de execução | Binário nativo, muito rápido. | Mais lento (irrelevante aqui). | Go (não importa) |

**Conclusão honesta (e autocrítica):** o único ponto onde Go realmente facilita é
a formatação automática (`gofmt`) — e isso é um detalhe pequeno perto da dor de
fazer o emissor produzir Go que *compile* (tipos explícitos, imports usados,
`int` vs `int64`). Em Python, "gerou → rodou" na maioria das vezes. Para
"o mais fácil", **Python**.

> **Alternativa ainda mais fácil (considere antes de codar o transpilador):**
> o Portugol Studio **já lê arquivos** com a biblioteca `Arquivos`
> (`inclua biblioteca Arquivos --> a`, `abrir_arquivo`, `ler_linha`,
> `fechar_arquivo`). Dá para escrever a regressão logística **direto em Portugol
> real**, sem transpilador nenhum — você lê o CSV linha a linha e quebra com a
> biblioteca `Texto`. Limitações: parsing de número é trabalhoso, é lento, e a
> ergonomia para ML é ruim. **Se o entregável do trabalho é "um transpilador",
> faça o transpilador (Python). Se o entregável é "treinar o modelo", talvez nem
> precise dele.** Decida isso primeiro.

---

## 2. Pergunta 2 — A spec antiga serve de base? (parcialmente)

**Sim, a arquitetura geral está correta e é reaproveitável.** O pipeline
`código → Lexer → Parser → AST → (análise) → Emissor → código-alvo` é o desenho
clássico e certo de um transpilador. As seções 6–10 (estrutura de pastas, tipos de
token, gramática BNF, nós da AST, tabela de símbolos) são um bom ponto de partida e
**continuam válidas** se você trocar o alvo para Python.

**Mas a base tem erros e excessos que precisam ser corrigidos:**

- **Algoritmo errado:** tudo é regressão *linear*. Seu objetivo é *logística*.
- **Sintaxe Portugol inventada e incorreta** (ver Seção 12): `ref` (o certo é `&`),
  `funcao vazio`, `escrevaf`, argumentos nomeados `separador=","` — nada disso
  existe no Portugol Studio real.
- **Código de exemplo que não compilaria** nem em Go (incompatibilidade
  array vs slice no `LerCSV`, `:=` gerando `int` onde se pedia `int64`).
- **Concorrência desnecessária** e mal especificada (a "análise de conflito de
  escrita" geraria falsos positivos no próprio exemplo dela).
- **Tamanho fixo** `X[10000][3]` para um CSV de tamanho desconhecido.

A lista detalhada e priorizada está na **Seção 12**. O resto deste documento é a
base corrigida e focada no seu objetivo.

---

## 3. Subconjunto de Portugol suportado (dialeto Studio, sintaxe real)

Implemente **apenas isto**. É o suficiente para a regressão logística e mantém o
parser pequeno.

### 3.1 Estrutura do programa
```portugol
programa {
  // variáveis globais e funções aqui
  funcao inicio() {
    // ponto de entrada
  }
}
```

### 3.2 Tipos
| Portugol | Python | Observação |
|---|---|---|
| `inteiro` | `int` | sem distinção int32/int64 — Python tem inteiro arbitrário |
| `real` | `float` | |
| `logico` | `bool` | `verdadeiro`→`True`, `falso`→`False` |
| `cadeia` | `str` | |
| `inteiro v[N]` (vetor) | `list` (`[0]*N`) | índice começa em **0** |
| `real m[L][C]` (matriz) | lista de listas | |

### 3.3 Declaração e atribuição
```portugol
real taxa = 0.01      // → taxa = 0.01
inteiro n             // → n = 0   (inicialize com zero-value)
real pesos[3]         // → pesos = [0.0, 0.0, 0.0]
x = x + 1             // → x = x + 1
```
**Regra crítica (corrige bug da spec antiga):** como Python é dinâmico, **não há
problema de `int` vs `int64`**. Gere atribuição simples. Para variáveis sem
inicializador, emita o "zero value" do tipo (`0`, `0.0`, `False`, `""`).

### 3.4 Funções e procedimentos
```portugol
funcao real sigmoide(real z) {        // com retorno
  retorne 1.0 / (1.0 + exp(-z))
}
funcao inicializar(real &v[], inteiro n) {   // sem retorno (procedimento) + por referência
  para (inteiro i = 0; i < n; i++) {
    v[i] = 0.0
  }
}
```
- `funcao TIPO nome(...)` → `def nome(...):` com `return`.
- `funcao nome(...)` (sem tipo) → procedimento, `def nome(...):` sem `return` de valor.
- **Referência:** o operador correto do Portugol Studio é **`&`** antes do nome do
  parâmetro (a spec antiga usava `ref`, que está errado). Em Python, **listas e
  matrizes já são passadas por referência** (são mutáveis), então `&v[]` não exige
  nada especial no emissor. Para escalares por referência (`real &x`), Python não
  tem isso nativamente — evite no subset, ou faça a função **retornar** o valor.
  Para regressão logística você não precisa de escalar por referência.

### 3.5 Controle de fluxo
```portugol
se (cond) { ... } senao se (cond) { ... } senao { ... }
enquanto (cond) { ... }
para (inteiro i = 0; i < n; i++) { ... }
```
Mapeiam para `if/elif/else`, `while`, e `for`. O `para` C-style com passo `i++` /
`i += k` vira `for i in range(inicio, fim, passo):` quando o padrão for simples, ou
um `while` equivalente no caso geral (mais fácil de emitir corretamente — comece
pelo `while`).

### 3.6 Operadores
Aritméticos `+ - * / %` iguais. **Atenção:** `/` em Python 3 é divisão real
(float), o que é exatamente o que você quer para ML. Para divisão inteira use `//`
(mas você quase não vai precisar). `^` (potência) → `** ` ou `math.pow`.
Relacionais iguais. Lógicos: `e`/`&&` → `and`, `ou`/`||` → `or`, `nao`/`!` → `not`.

### 3.7 Entrada/saída e builtins
| Portugol | Python |
|---|---|
| `escreva(a, b, ...)` | `print(a, b, ..., sep="", end="")` |
| `escreval(...)` | `print(...)` (com quebra de linha) |
| `leia(x)` | `x = input()` + conversão pelo tipo |
| `raiz(x)` | `math.sqrt(x)` |
| `exp(x)` | `math.exp(x)` |
| `potencia(b,e)` | `math.pow(b,e)` |
| `logaritmo(x)` | `math.log(x)` |
| `absoluto(x)` | `abs(x)` |
| `aleatorio()` | `random.random()` |

### 3.8 Builtins estendidos (o "runtime" do seu transpilador)
Estes **não** existem no Portugol original — são a sua extensão para viabilizar ML
com CSV. Implemente-os como funções Python num módulo `runtime_portugol.py` e
mapeie as chamadas direto para elas:

| Portugol (extensão) | Python (runtime) |
|---|---|
| `ler_csv(caminho, X, y)` → devolve nº de linhas | `ler_csv(caminho, X, y, sep=",", pular_cabecalho=True)` |
| `normalizar_zscore(X, n, f)` → devolve `(medias, desvios)` | idem (modifica `X` in-place) |
| `dividir_treino_teste(X, y, frac_teste)` | idem |
| `salvar_pesos(caminho, pesos, intercepto)` | idem |

> **Atenção às assinaturas:** todas as funções do runtime usam argumentos
> **posicionais** (sem argumentos nomeados, que não existem em Portugol). Os
> defaults (`sep`, `pular_cabecalho`, `frac_teste`) existem no Python para
> simplificar chamadas diretas, mas o transpilador sempre emite args posicionais.

---

## 4. A matemática da regressão logística (o que muda vs. linear)

A spec antiga implementava **regressão linear**. Aqui está o que precisa ser
diferente — e por quê:

| Conceito | Linear (spec antiga) | **Logística (você precisa)** |
|---|---|---|
| Previsão | `ŷ = w·x + b` | `ŷ = sigmoide(w·x + b)`, onde `sigmoide(z)=1/(1+e^-z)` → probabilidade em (0,1) |
| Rótulo `y` | número real qualquer | **0 ou 1** (classe) |
| Custo | MSE | **Log-loss** (entropia cruzada binária): `J = -1/N Σ [ y·ln(ŷ) + (1-y)·ln(1-ŷ) ]` |
| Gradiente | `(ŷ - y)·x` | `(ŷ - y)·x` — **igual em forma!** (essa é a parte boa) |
| Atualização | `w -= lr·grad` | igual |
| Métrica | MSE / R² | **acurácia**, e opcionalmente precisão/recall |
| Decisão final | — | classe = 1 se `ŷ ≥ 0.5`, senão 0 |

**Pontos práticos que a spec antiga ignora e são essenciais para a logística:**

1. **Normalização das features é obrigatória.** Sem padronizar (z-score:
   `(x - média)/desvio`), o `exp` satura e o treino não converge com taxas
   normais. A spec antiga tinha `Padronizar` no runtime mas **não usava** no
   exemplo. Use.
2. **Proteja o `log`:** `ln(0)` é `-infinito`. Faça *clipping* de `ŷ` em
   `[1e-15, 1 - 1e-15]` antes de calcular o custo.
3. **Não precisa de paralelismo.** Um CSV de aula (centenas a milhares de linhas)
   treina em sequência em milissegundos.

---

## 5. Arquitetura do transpilador (enxuta, alvo Python)

```
projeto/
├── transpilador.py        # CLI: lê .por, gera .py
├── lexer.py               # texto → lista de tokens
├── parser.py              # tokens → AST
├── ast_nodes.py           # classes dos nós (ProgramaNode, FuncaoNode, ...)
├── emissor.py             # AST → string de código Python (com indentação)
├── runtime_portugol.py    # ler_csv, normalizar_zscore, etc. (copiado p/ saída)
└── exemplos/
    ├── regressao_logistica.por
    └── dados.csv
```

Reaproveite das seções 7–9 da spec antiga: **categorias de token, gramática BNF e
nós de AST estão corretos**. Só:
- **remova** todos os tokens de concorrência (`TOKEN_PARALELO_PARA`, `_GOROUTINE`,
  `_CANAL`, `_MUTEX`, `_TRAVAR`, `_DESTRAVAR`, `_ENVIAR`, `_RECEBER`);
- **remova** os tokens do dialeto clássico (`<-`, `fimse`, `fimpara`, `algoritmo`,
  etc.) até a v2;
- a **análise semântica pode ser mínima**: por ser Python dinâmico, você não
  precisa de inferência de tipos completa para gerar código que roda. Basta uma
  tabela de símbolos simples para detectar "variável não declarada" (opcional).

**Dica de emissão (resolve a única desvantagem do Python):** mantenha um contador
de indentação no emissor e uma função `linha(texto)` que escreve
`"    " * nivel + texto + "\n"`. Aumente o nível ao entrar em bloco, diminua ao
sair. Isso elimina 90% dos bugs de indentação.

---

## 6. Runtime Python (`runtime_portugol.py`)

```python
import csv, math, random

def ler_csv(caminho, X, y, sep=",", pular_cabecalho=True):
    """Última coluna = rótulo (0/1). Preenche X (lista de listas) e y (lista).
    Limpa X e y antes de preencher — o tamanho declarado em Portugol é apenas
    um hint de tipo; o conteúdo é substituído pelas linhas reais do arquivo.
    Retorna o número de linhas lidas (n real, não o tamanho declarado)."""
    X.clear(); y.clear()
    with open(caminho, newline="", encoding="utf-8") as f:
        leitor = csv.reader(f, delimiter=sep)
        linhas = list(leitor)
    if pular_cabecalho and linhas:
        linhas = linhas[1:]
    for linha in linhas:
        if not linha:
            continue
        valores = [float(v) for v in linha]
        X.append(valores[:-1])
        y.append(float(valores[-1]))
    return len(y)

def normalizar_zscore(X, n, f):
    """Padroniza (z-score) cada coluna de X[0:n][0:f] in-place.
    Recebe n e f explicitamente (o transpilador não infere tamanhos).
    Retorna (medias, desvios) para futura desnormalização."""
    if n == 0 or f == 0:
        return [], []
    medias = [sum(X[i][j] for i in range(n)) / n for j in range(f)]
    desvios = []
    for j in range(f):
        var = sum((X[i][j] - medias[j])**2 for i in range(n)) / n
        desvios.append(math.sqrt(var) or 1.0)  # evita divisão por zero
    for i in range(n):
        for j in range(f):
            X[i][j] = (X[i][j] - medias[j]) / desvios[j]
    return medias, desvios

def dividir_treino_teste(X, y, frac_teste=0.2, semente=42):
    random.seed(semente)
    idx = list(range(len(y)))
    random.shuffle(idx)
    corte = int(len(y) * (1 - frac_teste))
    tr, te = idx[:corte], idx[corte:]
    return ([X[i] for i in tr], [y[i] for i in tr],
            [X[i] for i in te], [y[i] for i in te])

def salvar_pesos(caminho, pesos, intercepto):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(" ".join(str(p) for p in pesos) + "\n")
        f.write(str(intercepto) + "\n")
```

> Você pode escrever `normalizar_zscore`, `sigmoide` e até a divisão treino/teste
> **direto em Portugol** (mais educativo). O mínimo que precisa ser runtime é o
> `ler_csv` (parsing de arquivo). Comece com tudo no runtime; migre para Portugol
> conforme o transpilador amadurece.

---

## 7. Exemplo completo — Regressão logística em Portugol (sintaxe Studio real)

> Arquivo `regressao_logistica.por`. Usa só o subset da Seção 3 + os builtins
> estendidos. Sigmoide implementada em Portugol (usa `exp`). Assume CSV onde a
> última coluna é o rótulo 0/1.

```portugol
programa {

  // ===== Configuração =====
  inteiro NUM_FEATURES = 4
  inteiro EPOCAS       = 2000
  real    TAXA         = 0.1

  // ===== Dados e modelo (globais) =====
  // O tamanho declarado é um hint de tipo; ler_csv substitui o conteúdo
  // pelas linhas reais do CSV (X e y crescem dinamicamente em Python).
  real X[5000][4]      // features (preenchido por ler_csv)
  real y[5000]         // rótulos 0/1
  real pesos[4]
  real intercepto = 0.0
  inteiro N = 0        // nº real de linhas lido do CSV

  // sigmoide(z) = 1 / (1 + e^-z)
  funcao real sigmoide(real z) {
    retorne 1.0 / (1.0 + exp(-z))
  }

  // probabilidade prevista para a amostra i (valor em (0,1), NÃO a classe)
  // A classe é decidida depois: classe = 1 se prever(i) >= 0.5, senao 0.
  funcao real prever(inteiro i) {
    real z = intercepto
    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      z = z + pesos[j] * X[i][j]
    }
    retorne sigmoide(z)
  }

  // custo médio (log-loss) sobre o dataset
  funcao real custo() {
    real soma = 0.0
    para (inteiro i = 0; i < N; i++) {
      real p = prever(i)
      se (p < 0.0000000000001) { p = 0.0000000000001 }
      se (p > 0.9999999999999) { p = 0.9999999999999 }
      soma = soma - (y[i] * logaritmo(p) + (1.0 - y[i]) * logaritmo(1.0 - p))
    }
    retorne soma / N
  }

  // um passo de gradiente descendente sobre todo o dataset
  funcao treinar() {
    para (inteiro epoca = 0; epoca < EPOCAS; epoca++) {
      real grad_w[4]
      real grad_b = 0.0
      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        grad_w[j] = 0.0
      }

      para (inteiro i = 0; i < N; i++) {
        real erro = prever(i) - y[i]           // (ŷ - y)
        grad_b = grad_b + erro
        para (inteiro j = 0; j < NUM_FEATURES; j++) {
          grad_w[j] = grad_w[j] + erro * X[i][j]
        }
      }

      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        pesos[j] = pesos[j] - TAXA * (grad_w[j] / N)
      }
      intercepto = intercepto - TAXA * (grad_b / N)

      se (epoca % 200 == 0) {
        escreval("Epoca ", epoca, " | custo: ", custo())
      }
    }
  }

  // acurácia: fração de classes previstas corretamente
  funcao real acuracia() {
    inteiro acertos = 0
    para (inteiro i = 0; i < N; i++) {
      inteiro classe = 0
      se (prever(i) >= 0.5) { classe = 1 }
      se (classe == y[i]) { acertos = acertos + 1 }
    }
    retorne acertos / N
  }

  funcao inicio() {
    escreval("=== Regressao Logistica em Portugol ===")
    N = ler_csv("dados.csv", X, y)
    escreval("Linhas lidas: ", N)

    normalizar_zscore(X, N, NUM_FEATURES)   // padroniza as features (essencial!)

    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      pesos[j] = 0.0
    }
    intercepto = 0.0

    treinar()

    escreval("")
    escreval("Acuracia final: ", acuracia())
    escreval("Intercepto: ", intercepto)
    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      escreval("peso[", j, "] = ", pesos[j])
    }
    salvar_pesos("modelo.txt", pesos, intercepto)
  }
}
```

---

## 8. Python que o transpilador deve gerar

> Saída esperada de `regressao_logistica.por`. Note como o mapeamento é quase 1:1
> e **nenhuma conversão de tipo explícita** é necessária — essa é a vantagem do
> alvo Python.

```python
# GERADO AUTOMATICAMENTE — NÃO EDITE
import math
from runtime_portugol import ler_csv, normalizar_zscore, salvar_pesos

NUM_FEATURES = 4
EPOCAS = 2000
TAXA = 0.1

X = [[0.0] * 4 for _ in range(5000)]
y = [0.0] * 5000
pesos = [0.0] * 4
intercepto = 0.0
N = 0

def sigmoide(z):
    return 1.0 / (1.0 + math.exp(-z))

def prever(i):
    # Retorna a PROBABILIDADE (0..1), não a classe. Classe = 1 se >= 0.5.
    z = intercepto
    for j in range(0, NUM_FEATURES):
        z = z + pesos[j] * X[i][j]
    return sigmoide(z)

def custo():
    soma = 0.0
    for i in range(0, N):
        p = prever(i)
        if p < 0.0000000000001: p = 0.0000000000001
        if p > 0.9999999999999: p = 0.9999999999999
        soma = soma - (y[i] * math.log(p) + (1.0 - y[i]) * math.log(1.0 - p))
    return soma / N

def treinar():
    global intercepto
    for epoca in range(0, EPOCAS):
        grad_w = [0.0] * 4
        grad_b = 0.0
        for j in range(0, NUM_FEATURES):
            grad_w[j] = 0.0
        for i in range(0, N):
            erro = prever(i) - y[i]
            grad_b = grad_b + erro
            for j in range(0, NUM_FEATURES):
                grad_w[j] = grad_w[j] + erro * X[i][j]
        for j in range(0, NUM_FEATURES):
            pesos[j] = pesos[j] - TAXA * (grad_w[j] / N)
        intercepto = intercepto - TAXA * (grad_b / N)
        if epoca % 200 == 0:
            print("Epoca ", epoca, " | custo: ", custo(), sep="")

def acuracia():
    acertos = 0
    for i in range(0, N):
        classe = 0
        if prever(i) >= 0.5: classe = 1
        if classe == y[i]: acertos = acertos + 1
    return acertos / N

def inicio():
    global N, intercepto
    print("=== Regressao Logistica em Portugol ===")
    N = ler_csv("dados.csv", X, y)
    print("Linhas lidas: ", N, sep="")
    normalizar_zscore(X, N, NUM_FEATURES)
    for j in range(0, NUM_FEATURES):
        pesos[j] = 0.0
    intercepto = 0.0
    treinar()
    print("")
    print("Acuracia final: ", acuracia(), sep="")
    print("Intercepto: ", intercepto, sep="")
    for j in range(0, NUM_FEATURES):
        print("peso[", j, "] = ", pesos[j], sep="")
    salvar_pesos("modelo.txt", pesos, intercepto)

if __name__ == "__main__":
    inicio()
```

> **Detalhe de implementação que você não pode esquecer:** funções que *atribuem* a
> uma variável global (`intercepto`, `N`) precisam de `global intercepto` no início
> da função em Python. O emissor deve detectar atribuições a nomes globais dentro de
> uma função e emitir a declaração `global` correspondente. (Listas como `pesos`,
> `X`, `y` **não** precisam de `global` porque você as muta, não as reatribui.)

---

## 9. CLI do transpilador

```bash
python transpilador.py regressao_logistica.por           # gera regressao_logistica.py
python transpilador.py regressao_logistica.por --run     # gera e executa
python transpilador.py regressao_logistica.por --tokens  # debug: imprime tokens
python transpilador.py regressao_logistica.por --ast     # debug: imprime a AST
```
Ao gerar, copie `runtime_portugol.py` para o lado do `.py` de saída (ou garanta que
está no `PYTHONPATH`).

---

## 10. Roteiro de implementação incremental (faça nesta ordem)

Cada etapa produz algo que roda — não tente fazer tudo de uma vez.

1. **Lexer** + comando `--tokens`. Teste com `01_media_nota.por`.
2. **Parser + AST** só para: `programa`, `funcao inicio`, declaração de variável
   escalar, `escreva`/`escreval`, expressões aritméticas. Comando `--ast`.
3. **Emissor** para o que já parseia. Meta: transpilar e rodar `01_media_nota.por`.
4. Adicione **`se/senao`, `enquanto`, `para`**. Teste com um fatorial.
5. Adicione **vetores, matrizes e funções com parâmetros/retorno**.
6. Adicione os **builtins matemáticos** (`exp`, `logaritmo`, ...) e os
   **estendidos** (`ler_csv`, `normalizar_zscore`, `salvar_pesos`).
7. Transpile e rode o **`regressao_logistica.por`** completo. Fim.

---

## 11. Casos de teste mínimos

### 11.1 Formato do CSV esperado

O `ler_csv` assume:
- **Última coluna** = rótulo (0 ou 1 para regressão logística).
- Demais colunas = features (numéricas).
- Separador padrão: vírgula. Primeira linha é cabeçalho (ignorada por padrão).
- Todos os valores devem ser numéricos (sem categorias textuais — faça
  encoding manual antes, se precisar).

Exemplo `dados.csv` (linearmente separável, classe 1 se `2*x1 - x2 + 0.5 > 0`):
```csv
x1,x2,x3,x4,classe
1.0,2.0,3.0,1.0,1
0.5,3.0,1.0,2.0,0
2.0,1.0,0.5,1.0,1
-1.0,0.0,2.0,0.5,0
...
```

Script gerador de dados sintéticos (`gerar_dados.py`):
```python
import csv, random, math
random.seed(42)
N = 500
with open("dados.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["x1","x2","x3","x4","classe"])
    for _ in range(N):
        x = [random.uniform(-3, 3) for _ in range(4)]
        z = 2*x[0] - 1*x[1] + 0.5*x[2] - 0.3*x[3] + 0.5
        y = 1 if z > 0 else 0
        w.writerow([*x, y])
```

### 11.2 Testes unitários

- **Lexer:** `inteiro x = 42` → `[INTEIRO, IDENT(x), ASSIGN, INT(42)]`.
- **Emissor (ponta a ponta):** para cada `.por` de teste, transpile, rode e compare
  a saída com a esperada.
  - `media.por`: média de 2 números.
  - `fatorial.por`: fatorial iterativo (testa `para`).
  - `vetor.por`: somar elementos de um vetor.
- **Teste de ML (o que valida o projeto):** gere um CSV sintético linearmente
  separável (ex.: classe 1 se `2*x1 - x2 + 0.5 > 0`), com ~500 linhas. Critério de
  aprovação: **acurácia ≥ 0.95** após o treino. (Para regressão logística,
  acurácia é a métrica certa — não MSE.)

---

## 12. Erros e excessos da spec antiga (corrigidos aqui)

Auditoria crítica da spec original (Go + regressão linear, já apagada), por
gravidade. Mantida como registro do que mudou e por quê:

### Erros que quebram (não compilaria / não rodaria)
1. **`LerCSV` incompatível (Seção 14):** a função recebe `*[][]float64` (slice) mas
   o programa declara `X [10000][3]float64` (array fixo). Passar `&X` aí **não
   compila em Go**. → Corrigido usando estruturas dinâmicas (listas em Python).
2. **`:=` gera tipo errado (Seção 4.1):** a regra "tem valor inicial → use `:=`"
   produz `x := 10` (tipo `int` do Go), mas o mapa de tipos exige `int64`. Isso gera
   incompatibilidade de tipos com funções que esperam `int64`. Além disso, `:=` nem
   funciona para globais no nível do pacote. → Em Python o problema some.
3. **Análise de conflito do `paralelo_para` daria falso positivo no próprio
   exemplo:** `grad_w_parcial[w]` é escrita numa variável compartilhada (mesmo sendo
   índices disjuntos e seguros). A regra "erro se escreve em variável compartilhada"
   barraria o exemplo da própria spec. → Concorrência removida.

### Sintaxe Portugol incorreta/inventada
4. **`ref` não existe** no Portugol Studio — o correto é **`&`** antes do parâmetro.
   (Confirmado na doc oficial.)
5. **`funcao vazio`** não existe — procedimento é `funcao nome(...)` sem tipo.
6. **`escrevaf`** não existe; **argumentos nomeados** (`separador=","`,
   `pularCabecalho=verdadeiro`) não existem em Portugol. → Viraram builtins de
   runtime com assinatura posicional.
7. **`inclua biblioteca`** (a forma real de usar bibliotecas, ex. `Arquivos`,
   `Matematica`) nem é mencionada.

### Excesso de escopo (corta para simplificar)
8. **Toda a concorrência** (`paralelo_para`, `goroutine`, `canal`, `mutex`,
   `WaitGroup`, Map-Reduce): desnecessária para o objetivo, e a parte mais difícil
   e arriscada de implementar. Removida.
9. **Dois dialetos** (Studio + VisuAlg) ao mesmo tempo: dobra o trabalho do parser.
   Fique só no Studio.
10. **Detecção de "índice fora dos limites em tempo de transpilação", Kahan
    summation, avisos de overflow:** "nice to have" que não te aproximam do
    objetivo. Deixe para depois (ou nunca).

### Erro de algoritmo (o mais importante)
11. **Era regressão linear; você quer logística.** Muda previsão (sigmoide), custo
    (log-loss), métricas (acurácia) e exige **normalização** das features. Tudo
    corrigido nas Seções 4, 6 e 7.

---

## 13. Fontes

- [Funcao | Portugol Padrões](https://leonelsanchesdasilva.github.io/portugol-padroes/docs/portugol-studio/declaracoes/funcao.html) — referência usa `&`.
- [Exemplo oficial: parametros_referencia.por](https://github.com/UNIVALI-LITE-BACKUP/Portugol-Studio-Recursos/blob/master/exemplos/subrotinas/parametros_referencia.por)
- [Matriz | Portugol Padrões](https://leonelsanchesdasilva.github.io/portugol-padroes/docs/portugol-studio/declaracoes/matriz.html)
- [Bibliotecas | Portugol Padrões](https://leonelsanchesdasilva.github.io/portugol-padroes/docs/portugol-studio/bibliotecas/) — `inclua biblioteca Nome --> apelido`.
- [Exemplo oficial: biblioteca Arquivos](https://github.com/UNIVALI-LITE/Portugol-Studio/blob/master/ide/src/main/assets/exemplos/bibliotecas/arquivos/gravar_arquivo.por)
