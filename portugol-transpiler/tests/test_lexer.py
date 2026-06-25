"""Testes de lexer dos casos da Secao 11.2 da SPEC_DEFINITIVA.

Caso de referencia: `inteiro x = 42` -> [INTEIRO, IDENT(x), ASSIGN, INT(42)].
Inclui casos adicionais (reais, cadeias, logicos, operadores) para cobertura.
"""

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_DIR)

from lexer import TokenType, tokenize  # noqa: E402


def test_declaracao_inteiro_secao_11_2():
    tokens = tokenize("inteiro x = 42")
    assert [t.tipo for t in tokens[:4]] == [
        TokenType.INTEIRO,
        TokenType.IDENT,
        TokenType.ASSIGN,
        TokenType.INT_LIT,
    ]
    assert tokens[1].valor == "x"
    assert tokens[3].valor == "42"
    assert tokens[-1].tipo == TokenType.EOF


def test_declaracao_real():
    tokens = tokenize("real taxa = 0.01")
    assert tokens[0].tipo == TokenType.REAL
    assert tokens[3].tipo == TokenType.FLOAT_LIT
    assert tokens[3].valor == "0.01"


def test_literais_cadeia_e_logico():
    tokens = tokenize('cadeia s = "oi"')
    assert tokens[3].tipo == TokenType.STRING_LIT
    assert tokens[3].valor == "oi"
    assert tokenize("verdadeiro")[0].tipo == TokenType.BOOL_LIT
    assert tokenize("falso")[0].tipo == TokenType.BOOL_LIT


def test_operadores_aritmeticos_e_potencia():
    tipos = [t.tipo for t in tokenize("a + b - c * d / e % f ^ g")]
    assert TokenType.MAIS in tipos
    assert TokenType.POT in tipos
    assert TokenType.MOD in tipos


def test_posicao_linha_coluna():
    tokens = tokenize("inteiro x")
    assert tokens[0].linha == 1
    assert tokens[0].coluna == 1
    assert tokens[1].coluna == 9
