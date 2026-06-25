#!/usr/bin/env bash
# Roda toda a suite de testes do transpilador.
# Se o pacote `coverage` estiver disponivel, mede a cobertura de
# lexer.py / parser.py / emissor.py e exige o minimo de 80%.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

PY="${PYTHON:-python3}"

if "$PY" -c "import coverage" >/dev/null 2>&1; then
  echo ">> Rodando pytest com medicao de cobertura"
  "$PY" -m coverage run --source=. -m pytest tests/ "$@"
  "$PY" -m coverage report -m \
    --include="*/lexer.py,*/parser.py,*/emissor.py" \
    --fail-under=80
else
  echo ">> 'coverage' nao instalado; rodando pytest sem medicao de cobertura"
  echo ">> (instale com 'pip install coverage' para validar o minimo de 80%)"
  "$PY" -m pytest tests/ "$@"
fi
