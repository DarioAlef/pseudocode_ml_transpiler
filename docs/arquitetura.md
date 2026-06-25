# Transpiler Architecture

**For**: Contributors who want to understand the pipeline and extend the transpiler  
**Prerequisites**: Basic Python knowledge, familiarity with [Portugol Studio](https://www.univali.br/), and understanding of compilers (lexer/parser/AST)

---

## Pipeline Overview

The transpiler converts Portugol source code to Python through four sequential stages:

```
Portugol Source Code (string)
           ↓
       ┌─────────┐
       │  Lexer  │  Tokenization
       └────┬────┘
            ↓ (Token list)
       ┌─────────┐
       │ Parser  │  Syntax Analysis
       └────┬────┘
            ↓ (AST tree)
       ┌─────────┐
       │   AST   │  Representation
       └────┬────┘
            ↓ (Node objects)
       ┌─────────┐
       │ Emissor │  Code Generation
       └────┬────┘
            ↓ (Python string)
  Python Source Code (.py file)
```

**Data flows left-to-right only** — no feedback loops, purely linear pipeline.

---

## Stage 1: Lexer (Tokenização)

**Module**: `portugol-transpiler/lexer.py`

### Purpose
Scan the Portugol source code character-by-character and produce a list of tokens (keywords, identifiers, numbers, operators, etc.).

### Input
- Portugol source code as a single string

### Output
- List of `Token` objects with:
  - `type`: Token category (PROGRAMA, INTEIRO, IDENT, etc.)
  - `value`: The actual text (e.g., "inteiro", "x", "42")
  - `linha`: Line number (for error reporting)
  - `coluna`: Column number (for error reporting)

### Key Classes
- **`Lexer`**: Main tokenizer class; scans source and builds token list
- **`Token`**: Represents a single token with type and value
- **`TokenType`**: Enum of all token categories (PROGRAMA, INTEIRO, REAL, ABRE_CHAVE, etc.)

### Example
```
Input Portugol:
  inteiro x = 42

Output Tokens:
  [
    Token(type=INTEIRO, value='inteiro', linha=1, coluna=1),
    Token(type=IDENT, value='x', linha=1, coluna=9),
    Token(type=ASSIGN, value='=', linha=1, coluna=11),
    Token(type=INT, value='42', linha=1, coluna=13)
  ]
```

### When to Modify
- **Add new keywords** (e.g., `oportuno`): Add to `TokenType` enum, update keyword recognition in `Lexer.tokenize()`
- **Add new operators** (e.g., `>>`, `<<`): Add token type and recognition logic
- **Fix tokenization bugs**: Check scanning logic, multi-character operator handling

---

## Stage 2: Parser (Análise Sintática)

**Module**: `portugol-transpiler/parser.py`

### Purpose
Read the token stream and build an Abstract Syntax Tree (AST) by parsing according to Portugol grammar rules.

### Input
- List of Token objects from Lexer

### Output
- `ProgramaNode` (root AST node) containing:
  - Global variable declarations
  - Function declarations
  - The `funcao inicio()` entry point

### Key Classes
- **`Parser`**: Main parsing class; implements grammar rules and builds AST
- Grammar rules follow Portugol Studio syntax

### Example
```
Input Tokens:
  [INTEIRO, IDENT(x), ASSIGN, INT(42), ...]

Parsing Rules:
  programa → PROGRAMA ABRE_CHAVE ... FECHA_CHAVE
  declaracao → tipo IDENT [ASSIGN expresao]

Output AST:
  ProgramaNode(
    declaracoes=[DeclaracaoNode(tipo='inteiro', nome='x', valor=42)],
    funcao_inicio=FuncaoNode(nome='inicio', corpo=[...])
  )
```

### When to Modify
- **Add new statements** (e.g., `repita...ate`): Add grammar rule to Parser, create new AST node type
- **Add new control flow** (e.g., `escolha`): Extend Parser grammar, handle in Emissor
- **Fix parsing bugs**: Check grammar rules, operator precedence, lookahead logic

---

## Stage 3: AST (Árvore de Sintaxe Abstrata)

**Module**: `portugol-transpiler/ast_nodes.py`

### Purpose
Define the node types that represent Portugol program structure in a tree format.

### Input
- (Produced by Parser, not consumed from outside)

### Output
- Traversable tree of AST nodes that Emissor walks to generate Python code

### Key Classes
- **`Node`** (base): All AST nodes inherit from this
  - Attributes: `tipo` (data type), `nome` (identifier name)
- **`ProgramaNode`**: Root; contains declarations and entry function
- **`FuncaoNode`**: Function declaration; name, parameters, body
- **`DeclaracaoNode`**: Variable declaration; type, name, optional initial value
- **`AtribuicaoNode`**: Assignment statement; target and value
- **`SeNode`**: If statement; condition, then-block, optional else-block
- **`EnquantoNode`**: While loop; condition and body
- **`ParaNode`**: For loop; init, condition, increment, body
- **`ChamadaFuncaoNode`**: Function call; name and arguments
- **`ExpressaoNode`**: Arithmetic/logical expression; operator and operands

### Node Hierarchy
```
Node (abstract base)
  ├── ProgramaNode
  ├── FuncaoNode
  ├── DeclaracaoNode
  ├── AtribuicaoNode
  ├── SeNode
  ├── EnquantoNode
  ├── ParaNode
  ├── ChamadaFuncaoNode
  ├── RetornoNode
  └── ExpressaoNode
      ├── BinOpNode (binary operation)
      ├── UnOpNode (unary operation)
      ├── LiteralNode (number, string, boolean)
      └── IdentNode (variable reference)
```

### Example
```
Portugol:
  para (inteiro i = 0; i < 10; i++) {
    escreval(i)
  }

AST:
  ParaNode(
    inicializacao=DeclaracaoNode(tipo='inteiro', nome='i', valor=0),
    condicao=BinOpNode(op='<', esquerda=IdentNode('i'), direita=10),
    incremento=AtribuicaoNode(alvo='i', valor=BinOpNode(op='+', esquerda='i', direita=1)),
    corpo=[ChamadaFuncaoNode(nome='escreval', args=[IdentNode('i')])]
  )
```

### When to Modify
- **Add new node types**: Create new class inheriting from `Node`, implement any special attributes
- **Add new subtypes**: For example, if you support `para` with `passo k`, create `ParaComPassoNode`
- **Reorganize hierarchy**: Only if you're restructuring statement types

---

## Stage 4: Emissor (Geração de Código)

**Module**: `portugol-transpiler/emissor.py`

### Purpose
Walk the AST and emit Python code line-by-line, managing indentation and Python syntax.

### Input
- AST tree (root `ProgramaNode`)

### Output
- Complete Python source code as a string

### Key Classes
- **`Emissor`**: Main code generator class
  - Walks the AST recursively
  - Tracks indentation level
  - Builds Python code string

### Indentation Strategy
- Maintain `nivel_indentacao` counter (starts at 0)
- Each `{` in Portugol → increment level
- Each `}` in Portugol → decrement level
- Use `"    " * nivel` (4 spaces per level) for Python indentation
- Helper method: `linha(texto)` produces `indent + texto + "\n"`

### Example
```
AST:
  FuncaoNode(nome='sigmoide', params=[...], corpo=[...])

Generated Python:
  def sigmoide(z):
      return 1.0 / (1.0 + math.exp(-z))

Indentation:
  - Line 1: nivel=0 → "def sigmoide(z):"
  - Line 2: nivel=1 → "    return 1.0 / ..."
  - (After function) nivel=0 → next top-level code
```

### Critical: Global Variables
Functions that **assign to global variables** must emit `global varname` at the start:

```python
def treinar():
    global intercepto, pesos  # Must add this!
    intercepto = ...  # Modification
    pesos[j] = ...    # Mutation is OK without global
```

**Lexer/Parser must detect** which variables are reassigned vs. mutated, pass info to Emissor.

### When to Modify
- **Add new AST node** emission: Add method `emitir_[NodeType]()` that handles that node
- **Fix code generation**: Check indentation, Python syntax, variable scoping
- **Add new language features**: Ensure each feature's AST node has an emission method

---

## Stage 5: Semantic Analysis (Optional)

**Module**: `portugol-transpiler/semantic_analyzer.py`

### Purpose
Optional validation before code generation:
- Check variable declarations vs. usage
- Validate type compatibility (limited, since Python is dynamic)
- Detect scope errors

### When Used
Currently optional; run after parsing, before emission:
```python
parser = Parser(tokens)
ast = parser.parse()
analyzer = SemanticAnalyzer(ast)
analyzer.analyze()  # May raise SemanticError
emitter = Emissor(ast)
python_code = emitter.emitir()
```

### When to Modify
- Add type inference
- Add conflict detection for shared variable access (concurrency)
- Improve error messages

---

## Complete Data Flow Example

Trace a simple program through all 4 stages:

### Input Portugol
```portugol
programa {
  real taxa = 0.01
  
  funcao inicio() {
    escreval("Taxa: ", taxa)
  }
}
```

### Stage 1: Lexer Output
```
Tokens: [
  Token(PROGRAMA, 'programa'),
  Token(ABRE_CHAVE, '{'),
  Token(REAL, 'real'),
  Token(IDENT, 'taxa'),
  Token(ASSIGN, '='),
  Token(FLOAT, '0.01'),
  ...
  Token(ESCREVAL, 'escreval'),
  Token(ABRE_PAREN, '('),
  ...
]
```

### Stage 2: Parser Output (AST)
```
ProgramaNode(
  declaracoes=[
    DeclaracaoNode(tipo='real', nome='taxa', valor=LiteralNode(0.01))
  ],
  funcao_inicio=FuncaoNode(
    nome='inicio',
    corpo=[
      ChamadaFuncaoNode(
        nome='escreval',
        args=[
          LiteralNode('Taxa: '),
          IdentNode('taxa')
        ]
      )
    ]
  )
)
```

### Stage 3: AST (same as Stage 2 output)

### Stage 4: Emissor Output (Python)
```python
import math
from runtime_portugol import ...

taxa = 0.01

def inicio():
    print("Taxa: ", taxa, sep="", end="")

if __name__ == "__main__":
    inicio()
```

---

## Adding New Language Features

### Example: Support new operator `mod` (modulo)

**Step 1: Lexer** (portugol-transpiler/lexer.py)
- Add `MOD = auto()` to `TokenType` enum
- Add `'mod': TokenType.MOD` to keywords dictionary

**Step 2: Parser** (portugol-transpiler/parser.py)
- Add `mod` to binary operator precedence
- Handle `mod` in expression parsing (same as `*`, `/`)

**Step 3: AST** (portugol-transpiler/ast_nodes.py)
- No change needed — `BinOpNode` already supports any operator

**Step 4: Emissor** (portugol-transpiler/emissor.py)
- Add handling in binary operator emission:
  ```python
  if node.op == 'mod':
      return f"({left} % {right})"
  ```

**Step 5: Test**
```portugol
programa {
  funcao inicio() {
    inteiro resto = 17 mod 5
    escreval(resto)  // Should print 2
  }
}
```

---

## Performance Considerations

The transpiler is single-pass for each stage:
- **Lexer**: O(n) where n = source length (one scan)
- **Parser**: O(n) where n = token count (one pass + lookahead)
- **Emissor**: O(m) where m = AST node count (recursive walk)

Total: **O(n)** — linear in source code size.

**Not optimized for**:
- Very large programs (> 100K lines of Portugol)
- Highly complex nested structures

For typical educational examples (< 1K lines), performance is sub-second.

---

## Testing the Pipeline

### Unit Test: Lexer
```bash
python3 -c "
from portugol-transpiler.lexer import Lexer
l = Lexer('inteiro x = 42')
tokens = l.tokenize()
print(tokens)
"
```

### Unit Test: Parser
```bash
python3 -c "
from portugol-transpiler.lexer import Lexer
from portugol-transpiler.parser import Parser
l = Lexer('programa { funcao inicio() { } }')
tokens = l.tokenize()
p = Parser(tokens)
ast = p.parse()
print(ast)
"
```

### End-to-End Test
```bash
python3 portugol-transpiler/transpilador.py exercises_portugol/01_media_nota.por --run
```

---

## Next Steps

- **Want to add support for a new Portugol construct?** Follow the "Adding New Language Features" section
- **Need to fix a tokenization bug?** Check lexer.py
- **Confused about AST structure?** Read ast_nodes.py class definitions
- **Want to understand how Python is generated?** Study emitter.py methods

---

## References

- [Spec Definitiva](../SPEC_DEFINITIVA.md) — Complete language specification
- [Compiler Design](https://en.wikipedia.org/wiki/Compiler) — Background reading
- [Python AST module](https://docs.python.org/3/library/ast.html) — Reference implementation
