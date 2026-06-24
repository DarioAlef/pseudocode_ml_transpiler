"""CLI principal do transpilador Portugol -> Python.

Responsabilidade: ler um arquivo-fonte `.por` e orquestrar o pipeline de
transpilacao (lexer -> parser -> AST -> emissor) para gerar codigo Python.
Nesta fase de scaffold apenas a superficie de argumentos e o pedido de
ajuda (`--help`) estao implementados; as acoes de transpilacao sao no-op.
"""

import argparse
import sys


def main(argv=None):
    """Faz o parse dos argumentos da linha de comando.

    Os flags `--run`, `--tokens` e `--ast` sao declarados como no-op nesta
    fase; apenas a superficie de argumentos e `--help` sao funcionais agora.
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
        help="depuracao: imprime a lista de tokens (no-op nesta fase)",
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="depuracao: imprime a AST gerada (no-op nesta fase)",
    )

    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
