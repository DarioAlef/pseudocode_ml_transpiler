# Project Roadmap

**Goal**: Build a complete Portugol → Python transpiler that enables students to write ML algorithms in pseudocode.

**Current Status**: v1.1 — Core transpiler complete with logistic regression support  
**Next Milestone**: v1.2 — Enhanced error messages and documentation improvements

---

## Completed Features ✅

### v1.0 - Core Transpiler Foundation
- ✅ **Lexer**: Tokenize Portugol Studio syntax
- ✅ **Parser**: Build Abstract Syntax Tree from tokens
- ✅ **AST Nodes**: Full node hierarchy for program representation
- ✅ **Emissor**: Generate Python code from AST
- ✅ **CLI**: Command-line interface (`--tokens`, `--ast`, `--run`)

### v1.1 - ML & Builtins
- ✅ **Math Builtins**: `exp()`, `logaritmo()`, `raiz()`, `potencia()`
- ✅ **ML Builtins**: `ler_csv()`, `normalizar_zscore()`, `dividir_treino_teste()`
- ✅ **Logical Operators**: `e` (and), `ou` (or), `nao` (not)
- ✅ **Power Operator**: `^` for exponentiation
- ✅ **Regressão Logística**: Complete example implementation
- ✅ **Runtime Library**: `runtime_portugol.py` with utility functions
- ✅ **Documentation**: README, architecture guide, this roadmap

---

## Planned Features 🚀

### v1.2 - Enhanced Developer Experience
**Priority**: High | **Estimated**: 2-3 weeks | **Dependencies**: Core transpiler stable

#### Enhanced Error Messages
**Why it matters**: Current errors can be cryptic for new developers. Better messages accelerate learning.

- [ ] Add line/column information to error messages
- [ ] Provide suggestions for common mistakes (e.g., typos in keywords)
- [ ] Show context (surrounding lines) when reporting errors
- [ ] Create error codes for documentation reference (ERR-001, ERR-002, etc.)

**Example**:
```
Error on line 5, column 12:
  real x = 0.01
              ↓
Unexpected token: expected ';' but got EOF

Did you mean: `real x = 0.01`?
See ERR-005: Missing semicolon
```

#### Documentation Improvements
**Why it matters**: New contributors need clear guides.

- [ ] Add type inference documentation
- [ ] Document test structure and adding new test cases
- [ ] Create contributor onboarding guide
- [ ] Add API documentation for all public classes

---

### v1.3 - Multiple Portugol Dialects
**Priority**: Medium | **Estimated**: 4-5 weeks | **Dependencies**: Lexer/Parser refactoring

**Why it matters**: Support VisuAlg and "classic" Portugol variants to reach more students.

- [ ] **Dialect detection**: Auto-detect source dialect from syntax
- [ ] **VisuAlg Support**: 
  - Keywords: `algoritmo`, `inicio/fimalgoritmo`, `<-` assignment
  - Array syntax: `vetor[1..10]` (1-indexed)
  - Operators: `mod` (built-in, not `%`)
- [ ] **Classic Portugol**:
  - Alternative keyword sets
  - Different operator precedence rules
- [ ] **Compatibility layer**: Translate between dialects automatically
- [ ] **Tests**: Each dialect with 5-10 example programs

**Example**:
```bash
# Auto-detect and transpile:
python3 transpilador.py classic_program.por
# Output: "Detected dialect: VisuAlg 1.3"

# Or explicitly specify:
python3 transpilador.py classic_program.por --dialect visuAlg
```

---

### v1.4 - Optimization & Performance
**Priority**: Low | **Estimated**: 3-4 weeks | **Dependencies**: AST visitor pattern

**Why it matters**: Generated code should be efficient; teaches optimization concepts.

- [ ] **Constant Folding**: `1 + 2` → `3` at compile time
- [ ] **Dead Code Elimination**: Remove unused variables/expressions
- [ ] **Loop Unrolling**: Optimize small loops
- [ ] **Inlining**: Inline small functions automatically
- [ ] **Optimization Report**: Show what was optimized (`--opt-report`)

**Example**:
```portugol
// Input:
real x = (1 + 2) * 3

// Optimized output:
x = 9.0  # Constant folded during transpilation
```

---

### v2.0 - Concurrency Support (Future)
**Priority**: Low | **Estimated**: 6-8 weeks | **Dependencies**: Everything above

**Why it matters**: Teach concurrent programming concepts in pseudocode context.

⚠️ **Note**: Currently **deferred** — adds significant complexity. Revisit after v1.4.

- [ ] **Parallel For**: `paralelo_para (inteiro i = 0; i < n; i++)`
- [ ] **Thread Synchronization**: `mutex`, `travar`, `destravar`
- [ ] **Message Passing**: `canal` type, `enviar`, `receber`
- [ ] **WaitGroup Alternative**: Barrier synchronization
- [ ] **Race Condition Detection**: Warn about unsafe concurrent access
- [ ] **Runtime**: Use Python `threading` or `multiprocessing`

---

### v3.0 - Interactive Development (Future)
**Priority**: Low | **Estimated**: Future consideration

**Why it matters**: Interactive environment accelerates learning.

- [ ] **REPL Mode**: Read-Eval-Print-Loop for Portugol
- [ ] **Step Debugger**: Set breakpoints, step through execution
- [ ] **Variable Inspector**: Inspect state at any breakpoint
- [ ] **Web IDE**: Browser-based editor with live transpilation
- [ ] **Jupyter Integration**: `.ipynb` notebooks with Portugol cells

---

## Completed Milestones

### Milestone 1: Core Transpilation ✅
- Lexer, Parser, AST, Emissor complete
- All basic constructs supported
- CLI working with --tokens, --ast flags
- **Status**: COMPLETE (v1.0)

### Milestone 2: ML Support ✅
- Math and ML builtins implemented
- Regressão logística example working
- CSV I/O and normalization functions
- **Status**: COMPLETE (v1.1)

### Milestone 3: Documentation ✅
- README with examples
- Architecture guide
- Project roadmap
- Code docstrings
- **Status**: COMPLETE (v1.1)

---

## How to Contribute

### Pick a Feature
1. Look through **Planned Features** above
2. Check if it's marked as high priority
3. Verify dependencies are complete (listed under **Dependencies**)
4. Open an issue: "Working on: [Feature Name]"

### Understand the System
1. Read [Architecture Documentation](arquitetura.md)
2. Study the relevant module (`lexer.py`, `parser.py`, etc.)
3. Run existing tests to understand patterns

### Write Tests First (TDD)
1. Create test cases for your feature in `tests/`
2. Run tests — they should **fail** initially
3. Implement the feature
4. Tests should now **pass**

### Submit a PR
1. Include your test cases
2. Link to the roadmap item
3. Describe what changed and why
4. Request review from maintainers

---

## Release Timeline (Aspirational)

| Version | Features | Target Date | Status |
|---------|----------|------------|--------|
| v1.0 | Core transpiler | ✅ Shipped | Complete |
| v1.1 | ML support, docs | ✅ Shipped | Complete |
| v1.2 | Better errors | Q3 2026 | Planning |
| v1.3 | Multiple dialects | Q4 2026 | Not started |
| v1.4 | Optimization | Q1 2027 | Not started |
| v2.0 | Concurrency | Future | Deferred |
| v3.0 | Web IDE | Future | Not started |

---

## Design Principles

All features should follow these principles:

1. **Simplicity over features**: Each feature should be easy to understand
2. **Educational value**: Teach compiler/language concepts
3. **No external dependencies**: Stick to Python stdlib only
4. **Incremental development**: Complete features fully before moving to next
5. **Testing**: Every feature has test coverage
6. **Documentation**: Every feature is documented

---

## Known Limitations & Workarounds

### Limitation 1: No Multiple File Import
**Issue**: Cannot import functions from other `.por` files

**Workaround**: Write all code in single `.por` file or pre-process with a shell script

**Planned**: Will revisit in v2.0

### Limitation 2: No Object-Oriented Constructs
**Issue**: No classes, inheritance, polymorphism

**Workaround**: Use functions and data structures

**Planned**: May add in v2.0 as "structs" lightweight alternative

### Limitation 3: Limited String Manipulation
**Issue**: Minimal string builtin functions

**Workaround**: Transpile to Python, use Python string methods directly on generated code

**Planned**: Add string builtins in v1.3

---

## Metrics & Goals

### Adoption
- Goal: **100+ students** use transpiler by end of 2026
- Current: ~10 active users
- Tracking: Stars on GitHub, contributions

### Code Quality
- Goal: **100% test coverage** of core functionality
- Current: ~80% coverage (lexer, parser, emissor)
- Tracking: CI/CD pipeline reports

### Performance
- Goal: **< 100ms** transpilation time for programs < 1000 lines
- Current: ~50ms average
- Tracking: Benchmark suite in CI

### Documentation
- Goal: **Every public API documented** with examples
- Current: Core APIs documented, some gaps in advanced features
- Tracking: Doc coverage in CI

---

## Contact & Questions

- **Found a bug?** Open an issue
- **Want to contribute?** See [CONTRIBUTING.md](../CONTRIBUTING.md) (coming soon)
- **Have a feature idea?** Discuss in GitHub Discussions
- **Need help?** Read [Architecture Docs](arquitetura.md) or ask in Issues

---

**Last Updated**: 2026-06-25  
**Maintained By**: Dario Lima & Contributors
