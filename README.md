# Portugol Transpiler

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A Python transpiler that converts [Portugol Studio](https://www.univali.br/en/) pseudocode into executable Python, enabling students to learn compiler design while solving real ML problems.

**📘 Main Goal**: Write and train a logistic regression classifier in Portugol by reading data from CSV files.

---

## Quick Start

Get the transpiler running in under 5 minutes:

### 1. Install Python 3.10+

```bash
python3 --version  # Must be 3.10 or higher
```

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/pseudocode_ml_transpiler.git
cd pseudocode_ml_transpiler
```

### 3. Run Your First Example

Create a simple Portugol program (or use the example below):

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

Transpile and run:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --run
```

Expected output after you input two grades:
```
A média é: 7.5
```

---

## Usage Examples

### Basic Transpilation

Generate Python code from Portugol:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por
```

This creates a `.py` file in `portugol_out/` directory.

### Debug: View Tokens

See how the lexer tokenizes your code:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --tokens
```

Output example:
```
[Token(type=PROGRAMA, value='programa'), Token(type=ABRE_CHAVE, value='{'), ...]
```

### Debug: View AST

See the Abstract Syntax Tree produced by the parser:

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --ast
```

### Transpile to Custom Directory

```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --output-dir ./my_output/
```

---

## Supported Portugol Subset

This transpiler implements **Portugol Studio** dialect with the following features:

### Types
- `inteiro` → Python `int`
- `real` → Python `float`
- `logico` → Python `bool` (`verdadeiro`/`falso`)
- `cadeia` → Python `str`
- Vectors: `inteiro v[10]` → Python `list`
- Matrices: `real m[5][3]` → Python nested `list`

### Program Structure
```portugol
programa {
  // global variables
  inteiro x = 42
  
  funcao inicio() {
    // entry point - required
  }
}
```

### Control Flow
- **If/Else**: `se (cond) { ... } senao se { ... } senao { ... }`
- **While**: `enquanto (cond) { ... }`
- **For**: `para (inteiro i = 0; i < n; i++) { ... }`

### Functions & Procedures
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

### Operators & Built-ins

**Arithmetic**: `+ - * / %`  
**Power**: `^` → Python `**`  
**Logical**: `e` (and), `ou` (or), `nao` (not)  

**Built-in Functions**:
- I/O: `escreva()`, `escreval()`, `leia()`
- Math: `raiz()`, `exp()`, `logaritmo()`, `absoluto()`, `aleatorio()`
- **ML Extensions** (custom to transpiler):
  - `ler_csv()` - Read CSV data
  - `normalizar_zscore()` - Z-score normalization
  - `dividir_treino_teste()` - Train/test split
  - `salvar_pesos()` - Save model weights

**For complete specification**, see [SPEC_DEFINITIVA.md](SPEC_DEFINITIVA.md).

---

## Complete Example: Logistic Regression

The motivating use case for this transpiler is training a logistic regression classifier:

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
    // ... training loop ...
  }
}
```

**Full example**: [exemplos/regressao_logistica.por](portugol-transpiler/exemplos/regressao_logistica.por)

---

## Architecture

The transpiler follows a classic compiler pipeline:

```
Portugol Source (.por)
        ↓
    [Lexer] - Tokenization
        ↓
   [Parser] - Syntax Analysis
        ↓
     [AST] - Abstract Syntax Tree
        ↓
  [Emissor] - Code Generation
        ↓
  Python Code (.py)
```

**Learn more**: [Architecture Documentation](docs/arquitetura.md)

---

## Project Roadmap

See what's planned and completed:

- ✅ **v1.0-v1.1**: Lexer, Parser, AST, Code Generation, Math Builtins, ML Support
- 🚀 **Planned**: Multiple dialects, Enhanced error messages, Optimization passes
- 🔮 **Future**: Concurrency support, Interactive REPL, Web IDE

**Full roadmap**: [docs/roadmap.md](docs/roadmap.md)

---

## Contributing

We welcome contributions! Here's how:

1. **Pick a feature** from the [roadmap](docs/roadmap.md)
2. **Understand the architecture** by reading [Architecture Docs](docs/arquitetura.md)
3. **Write tests** for your changes
4. **Submit a PR** with your implementation

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines (coming soon).

---

## License

MIT License - see LICENSE file for details

---

## Questions?

- 📖 Read the [Architecture Documentation](docs/arquitetura.md)
- 🗺️ Check the [Project Roadmap](docs/roadmap.md)
- 📚 Reference the [Spec](SPEC_DEFINITIVA.md)
- 💬 Open an issue on GitHub

---

**Made with ❤️ for students learning compilers and ML**
