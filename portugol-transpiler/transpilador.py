"""CLI principal do transpilador Portugol -> Python.

Responsabilidade: ler um arquivo-fonte `.por` e orquestrar o pipeline de
transpilacao (lexer -> parser -> AST -> emissor) para gerar codigo Python.
Modos:
  - <arquivo>          : gera saida/<nome>.py + copia runtime_portugol.py
  - <arquivo> --run    : gera e executa o .py (cwd=saida/)
  - <arquivo> --tokens : depuracao, imprime a lista de tokens
  - <arquivo> --ast    : depuracao, imprime a AST indentada
Erros lexicos/sintaticos -> mensagem com linha/coluna em stderr, retorno 1.
"""

import argparse
import os
import pprint
import shutil
import subprocess
import sys

from lexer import ErroLexico, tokenize
from parser import ErroSintatico
from parser import parse as parser_parse
from emissor import emitir


def _imprimir_tokens(caminho):
    """Le `caminho`, tokeniza e imprime um token por linha (FR-016, SC-004)."""
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()
    for token in tokenize(codigo):
        print(f"{token.tipo.name} {token.valor!r} (L{token.linha},C{token.coluna})")
    return 0


def _imprimir_ast(caminho):
    """Le `caminho`, parseia e imprime a AST indentada (FR-021, SC-004)."""
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()
    ast = parser_parse(tokenize(codigo))
    print(pprint.pformat(ast))
    return 0


def _gerar_py(caminho):
    """Le .por, transpila e escreve saida/<nome>.py + copia runtime.

    Retorna o caminho absoluto do .py gerado. Cria saida/ se necessario.
    """
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()
    ast = parser_parse(tokenize(codigo))
    py = emitir(ast)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    saida_dir = os.path.join(base_dir, "saida")
    os.makedirs(saida_dir, exist_ok=True)

    nome_base = os.path.splitext(os.path.basename(caminho))[0]
    caminho_py = os.path.join(saida_dir, f"{nome_base}.py")
    with open(caminho_py, "w", encoding="utf-8") as f:
        f.write(py)

    runtime_src = os.path.join(base_dir, "runtime_portugol.py")
    runtime_dst = os.path.join(saida_dir, "runtime_portugol.py")
    if os.path.exists(runtime_src):
        shutil.copyfile(runtime_src, runtime_dst)

    return caminho_py


def _transpilar(caminho):
    """Gera o .py e imprime o caminho gerado no stdout. Retorna 0."""
    caminho_py = _gerar_py(caminho)
    print(caminho_py)
    return 0


def _transpilar_e_rodar(caminho):
    """Gera o .py e o executa via subprocess com cwd=saida/.

    Encaminha stdin/stdout/stderr; retorna o codigo de saida do filho.
    """
    caminho_py = _gerar_py(caminho)
    print(caminho_py)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    saida_dir = os.path.join(base_dir, "saida")
    nome_arq = os.path.basename(caminho_py)
    resultado = subprocess.run(
        [sys.executable, nome_arq],
        cwd=saida_dir,
    )
    return resultado.returncode


def main(argv=None):
    """Faz o parse dos argumentos da linha de comando e despacha a acao."""
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
        help="gera e executa o codigo Python resultante",
    )
    parser.add_argument(
        "--tokens",
        action="store_true",
        help="depuracao: imprime a lista de tokens do arquivo",
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="depuracao: imprime a AST gerada pelo parser",
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

    if args.ast:
        if not args.arquivo:
            parser.error("--ast requer um arquivo .por")
        try:
            return _imprimir_ast(args.arquivo)
        except (ErroLexico, ErroSintatico) as erro:
            print(str(erro), file=sys.stderr)
            return 1

    if args.arquivo:
        try:
            if args.run:
                return _transpilar_e_rodar(args.arquivo)
            return _transpilar(args.arquivo)
        except (ErroLexico, ErroSintatico) as erro:
            print(str(erro), file=sys.stderr)
            return 1
        except FileNotFoundError as erro:
            print(str(erro), file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
