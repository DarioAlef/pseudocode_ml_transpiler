"""Testes de parser dos casos da Secao 11.2 da SPEC_DEFINITIVA.

Parseia os programas de teste (media/fatorial/vetor) e valida a forma da AST:
declaracoes com inicializacao, laco `para` e vetores com indexacao.
"""

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_DIR)

from ast_nodes import (  # noqa: E402
    AssignNode,
    ForStmtNode,
    IndexExprNode,
    ProgramNode,
    VarDeclNode,
)
from lexer import tokenize  # noqa: E402
from parser import parse  # noqa: E402

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _parse_arquivo(nome):
    with open(os.path.join(TESTS_DIR, nome), encoding="utf-8") as f:
        return parse(tokenize(f.read()))


def _corpo_inicio(prog):
    inicio = next(f for f in prog.funcoes if f.nome == "inicio")
    return inicio.body.stmts


def test_media_declaracao_com_init():
    prog = _parse_arquivo("media.por")
    assert isinstance(prog, ProgramNode)
    stmts = _corpo_inicio(prog)
    decls = [s for s in stmts if isinstance(s, VarDeclNode)]
    assert any(d.nome == "media" and d.init is not None for d in decls)


def test_fatorial_tem_laco_para():
    prog = _parse_arquivo("fatorial.por")
    stmts = _corpo_inicio(prog)
    assert any(isinstance(s, ForStmtNode) for s in stmts)


def test_vetor_declaracao_e_indexacao():
    prog = _parse_arquivo("vetor.por")
    stmts = _corpo_inicio(prog)
    vet = next(s for s in stmts if isinstance(s, VarDeclNode) and s.nome == "v")
    assert vet.tipo.is_array
    atribuicoes_indexadas = [
        s for s in stmts
        if isinstance(s, AssignNode) and isinstance(s.alvo, IndexExprNode)
    ]
    assert len(atribuicoes_indexadas) >= 5


def test_para_tem_init_cond_post():
    prog = _parse_arquivo("fatorial.por")
    laco = next(s for s in _corpo_inicio(prog) if isinstance(s, ForStmtNode))
    assert laco.init is not None
    assert laco.cond is not None
    assert laco.post is not None
