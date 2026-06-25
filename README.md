# Transpilador Portugol

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Licença: MIT](https://img.shields.io/badge/license-MIT-green)

Um transpilador Python que converte pseudocódigo do [Portugol Studio](https://www.univali.br/en/) em código Python executável, permitindo que estudantes aprendam sobre construção de compiladores enquanto resolvem problemas reais de Machine Learning (ML).

**📘 Objetivo Principal**: Escrever e treinar um classificador de Regressão Logística em Portugol lendo dados de arquivos CSV.

---

## Início Rápido

Coloque o transpilador para rodar em menos de 5 minutos:

### 1. Instale Python 3.10+

```bash
python3 --version  # Deve ser 3.10 ou superior
```

### 2. Clone o Repositório

```bash
git clone https://github.com/your-username/pseudocode_ml_transpiler.git
cd pseudocode_ml_transpiler
```

### 3. Rode Seu Primeiro Exemplo

Crie um programa simples em Portugol (ou use o exemplo abaixo):

```portugol
programa {
  funcao inicio() {
    real nota_1
    real nota_2
    real media

    escreva("Digite a primeira nota:")
    leia(nota_1)
    escreva("Digite a segunda nota:")
    leia(nota_2)

    media = (nota_1 + nota_2) / 2

    escreval("A média é: ", media)
  }
}
```

Transpile e execute:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --run
```

Saída esperada após você inserir duas notas:
```
A média é: 7.5
```

---

## Exemplos de Uso

### Transpilação Básica

Gere código Python a partir de Portugol:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por
```

Isso cria um arquivo `.py` no diretório `portugol_out/`.

### Depuração: Ver Tokens

Veja como o Lexer tokeniza o seu código:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --tokens
```

Exemplo de saída:
```
[Token(type=PROGRAMA, value='programa'), Token(type=ABRE_CHAVE, value='{'), ...]
```

### Depuração: Ver AST

Veja a Abstract Syntax Tree produzida pelo Parser:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --ast
```

### Transpilar para um Diretório Customizado

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --output-dir ./my_output/
```

---

## Subconjunto de Portugol Suportado

Este transpilador implementa o dialeto do **Portugol Studio** com as seguintes funcionalidades:

### Tipos
- `inteiro` → Python `int`
- `real` → Python `float`
- `logico` → Python `bool` (`verdadeiro`/`falso`)
- `cadeia` → Python `str`
- Vetores: `inteiro v[10]` → Python `list`
- Matrizes: `real m[5][3]` → Python nested `list`

### Estrutura do Programa
```portugol
programa {
  // variáveis globais
  inteiro x = 42
  
  funcao inicio() {
    // ponto de entrada - obrigatório
  }
}
```

### Controle de Fluxo
- **If/Else**: `se (cond) { ... } senao se { ... } senao { ... }`
- **While**: `enquanto (cond) { ... }`
- **For**: `para (inteiro i = 0; i < n; i++) { ... }`

### Funções & Procedimentos
```portugol
funcao real sigmoide(real z) {
  retorne 1.0 / (1.0 + exp(-z))
}

funcao inicializar(real &v[], inteiro n) {
  para (inteiro i = 0; i < n; i++) {
    v[i] = 0.0
  }
}
```

### Operadores & Built-ins

**Aritméticos**: `+ - * / %`  
**Potência**: `^` → Python `**`  
**Lógicos**: `e` (and), `ou` (or), `nao` (not)  

**Funções Built-in**:
- I/O: `escreva()`, `escreval()`, `leia()`
- Matemática: `raiz()`, `exp()`, `logaritmo()`, `absoluto()`, `aleatorio()`
- **Extensões de ML** (customizadas para o transpilador):
  - `ler_csv()` - Ler dados de um CSV
  - `normalizar_zscore()` - Normalização Z-score
  - `dividir_treino_teste()` - Divisão treino/teste (Train/test split)
  - `salvar_pesos()` - Salvar pesos do modelo

**Para a especificação completa**, veja [SPEC_DEFINITIVA.md](SPEC_DEFINITIVA.md).

---

## Exemplo Completo: Regressão Logística

O caso de uso motivador para este transpilador é o treinamento de um classificador de Regressão Logística:

```portugol
programa {
  inteiro NUM_FEATURES = 4
  inteiro EPOCAS = 2000
  real TAXA = 0.1
  
  real X[5000][4]
  real y[5000]
  real pesos[4]
  real intercepto = 0.0
  
  funcao real sigmoide(real z) {
    retorne 1.0 / (1.0 + exp(-z))
  }
  
  funcao inicio() {
    inteiro N = ler_csv("data.csv", X, y)
    // ... loop de treinamento ...
  }
}
```

**Exemplo completo**: [exemplos/regressao_logistica.por](portugol-transpiler/exemplos/regressao_logistica.por)

---

## Arquitetura

O transpilador segue um pipeline clássico de compiladores:

```
Código Fonte em Portugol (.por)
        ↓
     [Lexer] - Tokenização
        ↓
    [Parser] - Análise Sintática
        ↓
      [AST] - Abstract Syntax Tree
        ↓
   [Emissor] - Geração de Código
        ↓
 Código Python (.py)
```

**Saiba mais**: [Documentação da Arquitetura](docs/arquitetura.md)

---

## Roadmap do Projeto

Veja o que está planejado e concluído:

- ✅ **v1.0-v1.1**: Lexer, Parser, AST, Geração de Código, Built-ins Matemáticos, Suporte a ML
- 🚀 **Planejado**: Múltiplos dialetos, Mensagens de erro aprimoradas, Passos de otimização
- 🔮 **Futuro**: Suporte a concorrência, REPL Interativo, Web IDE

**Roadmap completo**: [docs/roadmap.md](docs/roadmap.md)

---

## Contribuindo

Nós damos boas-vindas a contribuições! Veja como:

1. **Escolha uma funcionalidade** do [roadmap](docs/roadmap.md)
2. **Entenda a arquitetura** lendo a [Documentação da Arquitetura](docs/arquitetura.md)
3. **Escreva testes** para as suas alterações
4. **Envie um PR** com a sua implementação

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para diretrizes detalhadas (em breve).

---

## Licença

Licença MIT - veja o arquivo LICENSE para detalhes

---

## Dúvidas?

- 📖 Leia a [Documentação da Arquitetura](docs/arquitetura.md)
- 🗺️ Verifique o [Roadmap do Projeto](docs/roadmap.md)
- 📚 Consulte a [Especificação](SPEC_DEFINITIVA.md)
- 💬 Abra uma issue no GitHub

---

**Feito com ❤️ para estudantes aprendendo sobre compiladores e ML**
