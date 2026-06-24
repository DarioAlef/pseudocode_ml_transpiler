"""CLI principal do transpilador Portugol -> Python.

Responsabilidade: ler um arquivo-fonte `.por` e orquestrar o pipeline de
transpilacao (lexer -> parser -> AST -> emissor) para gerar codigo Python.
Nesta fase, `--tokens` imprime a lista de tokens (modo de depuracao); as
demais acoes de transpilacao permanecem reservadas para fases futuras.
"""

import argparse
import sys

from lexer import ErroLexico, tokenize


def _imprimir_tokens(caminho):
    """Le `caminho`, tokeniza e imprime um token por linha (FR-016, SC-004)."""
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()
    for token in tokenize(codigo):
        print(f"{token.tipo.name} {token.valor!r} (L{token.linha},C{token.coluna})")
    return 0


def main(argv=None):
    """Faz o parse dos argumentos da linha de comando.

    Os flags `--run` e `--ast` permanecem no-op; `--tokens` imprime os
    tokens do arquivo informado. `--help` e a superficie de argumentos
    sao preservados do scaffold.
    """
    parser = argparse.ArgumentParser(
        prog="transpilador.py",
        description="Transpilador Portugol -> Python.",
    )
    parser.add_argument(
        "arquivo",
        nargs="?",
        help="arquivo-fonte .por a ser transpilado (opcional nesta fase)",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="gera e executa o codigo Python resultante (no-op nesta fase)",
    )
    parser.add_argument(
        "--tokens",
        action="store_true",
        help="depuracao: imprime a lista de tokens do arquivo",
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="depuracao: imprime a AST gerada (no-op nesta fase)",
    )

    args = parser.parse_args(argv)

    if args.tokens:
        if not args.arquivo:
            parser.error("--tokens requer um arquivo .por")
        try:
            return _imprimir_tokens(args.arquivo)
        except ErroLexico as erro:
            print(str(erro), file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
