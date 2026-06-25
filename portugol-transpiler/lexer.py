"""Lexer do transpilador Portugol -> Python.

Responsabilidade: converter o texto-fonte de um programa `.por` em uma
lista ordenada de tokens classificados. Scanner de passe unico com
lookahead de 1 caractere, rastreio de linha/coluna (1-based) e emissao
de `EOF` ao final. Cobre o subset Portugol Studio (FR-003).
"""

import dataclasses
import enum


class TokenType(enum.Enum):
    """Categorias de token do subset Portugol Studio."""

    INTEIRO = "inteiro"
    REAL = "real"
    LOGICO = "logico"
    CADEIA = "cadeia"

    PROGRAMA = "programa"
    FUNCAO = "funcao"
    INICIO = "inicio"
    RETORNE = "retorne"

    SE = "se"
    SENAO = "senao"
    ENQUANTO = "enquanto"
    PARA = "para"
    INCLUA = "inclua"
    BIBLIOTECA = "biblioteca"
    ESCOLHA = "escolha"
    CASO = "caso"
    PARE = "pare"
    CONTRARIO = "contrario"

    INT_LIT = "INT_LIT"
    FLOAT_LIT = "FLOAT_LIT"
    STRING_LIT = "STRING_LIT"
    BOOL_LIT = "BOOL_LIT"

    IDENT = "IDENT"

    MAIS = "+"
    MENOS = "-"
    MULT = "*"
    DIV = "/"
    MOD = "%"
    POT = "^"
    ASSIGN = "="
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    AND = "&&"
    OR = "||"
    NOT = "!"
    INC = "++"
    DEC = "--"
    AMP = "&"

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    VIRGULA = ","
    PONTO_VIRGULA = ";"
    DOIS_PONTOS = ":"
    PONTO = "."
    SETA = "-->"

    EOF = "EOF"


@dataclasses.dataclass
class Token:
    """Unidade lexica reconhecida no texto-fonte (FR-002).

    Igualdade por todos os campos (fornecida por @dataclass), permitindo
    asserts diretos sobre listas de tokens.
    """

    tipo: TokenType
    valor: str
    linha: int
    coluna: int


class ErroLexico(Exception):
    """Erro de analise lexica com localizacao (FR-015, SC-006).

    Lanca em caractere ilegal, string nao terminada e comentario de
    bloco nao terminado. Carrega `linha`/`coluna` do caractere ofensor.
    """

    def __init__(self, linha, coluna, mensagem):
        self.linha = linha
        self.coluna = coluna
        self.mensagem = mensagem
        super().__init__(f"Erro lexico na linha {linha}, coluna {coluna}: {mensagem}")


PALAVRAS_CHAVE = {
    "inteiro": TokenType.INTEIRO,
    "real": TokenType.REAL,
    "logico": TokenType.LOGICO,
    "cadeia": TokenType.CADEIA,
    "programa": TokenType.PROGRAMA,
    "funcao": TokenType.FUNCAO,
    "inicio": TokenType.INICIO,
    "retorne": TokenType.RETORNE,
    "se": TokenType.SE,
    "senao": TokenType.SENAO,
    "enquanto": TokenType.ENQUANTO,
    "para": TokenType.PARA,
    "verdadeiro": TokenType.BOOL_LIT,
    "falso": TokenType.BOOL_LIT,
    "e": TokenType.AND,
    "ou": TokenType.OR,
    "nao": TokenType.NOT,
    "inclua": TokenType.INCLUA,
    "biblioteca": TokenType.BIBLIOTECA,
    "escolha": TokenType.ESCOLHA,
    "caso": TokenType.CASO,
    "pare": TokenType.PARE,
    "contrario": TokenType.CONTRARIO,
}

_OPERADORES_3CHAR = {
    "-->": TokenType.SETA,
}

_OPERADORES_2CHAR = {
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "<=": TokenType.LE,
    ">=": TokenType.GE,
    "&&": TokenType.AND,
    "||": TokenType.OR,
    "++": TokenType.INC,
    "--": TokenType.DEC,
}

_OPERADORES_1CHAR = {
    "+": TokenType.MAIS,
    "-": TokenType.MENOS,
    "*": TokenType.MULT,
    "/": TokenType.DIV,
    "%": TokenType.MOD,
    "^": TokenType.POT,
    "=": TokenType.ASSIGN,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "!": TokenType.NOT,
    "&": TokenType.AMP,
}

_PONTUACAO = {
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ",": TokenType.VIRGULA,
    ";": TokenType.PONTO_VIRGULA,
    ":": TokenType.DOIS_PONTOS,
    ".": TokenType.PONTO,
}

_LETRA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
_DIGITO = "0123456789"


class Lexer:
    """Scanner de passe unico sobre o texto-fonte Portugol.

    Percorre `codigo` caractere a caractere, descartando espacos e
    comentarios, rastreando linha/coluna e emitindo tokens terminados
    em `EOF`. Invariante: `pos` sempre avanca a cada iteracao (SC-006).
    """

    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    def _fim(self):
        return self.pos >= len(self.codigo)

    def _atual(self):
        if self._fim():
            return ""
        return self.codigo[self.pos]

    def _proximo(self):
        if self.pos + 1 >= len(self.codigo):
            return ""
        return self.codigo[self.pos + 1]

    def _avancar(self):
        caractere = self._atual()
        self.pos += 1
        if caractere == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1

    def _pular_espacos(self):
        while not self._fim():
            caractere = self._atual()
            if caractere in " \t\r\n":
                self._avancar()
            elif caractere == "/" and self._proximo() == "/":
                self._pular_comentario_linha()
            elif caractere == "/" and self._proximo() == "*":
                self._pular_comentario_bloco()
            else:
                break

    def _pular_comentario_linha(self):
        self._avancar()
        self._avancar()
        while not self._fim() and self._atual() != "\n":
            self._avancar()

    def _pular_comentario_bloco(self):
        linha = self.linha
        coluna = self.coluna
        self._avancar()
        self._avancar()
        while not self._fim():
            if self._atual() == "*" and self._proximo() == "/":
                self._avancar()
                self._avancar()
                return
            self._avancar()
        raise ErroLexico(
            linha, coluna, "comentario de bloco nao terminado"
        )

    def _ler_numero(self):
        linha = self.linha
        coluna = self.coluna
        inicio = self.pos
        while not self._fim() and self._atual() in _DIGITO:
            self._avancar()
        eh_real = False
        proximo = self._proximo()
        if self._atual() == "." and proximo and proximo in _DIGITO:
            eh_real = True
            self._avancar()
            while not self._fim() and self._atual() in _DIGITO:
                self._avancar()
        valor = self.codigo[inicio:self.pos]
        tipo = TokenType.FLOAT_LIT if eh_real else TokenType.INT_LIT
        return Token(tipo, valor, linha, coluna)

    def _ler_cadeia(self):
        linha = self.linha
        coluna = self.coluna
        self._avancar()
        chars = []
        while not self._fim():
            caractere = self._atual()
            if caractere == '"':
                self._avancar()
                return Token(TokenType.STRING_LIT, "".join(chars), linha, coluna)
            chars.append(caractere)
            self._avancar()
        raise ErroLexico(linha, coluna, "cadeia nao terminada")

    def _ler_identificador(self):
        linha = self.linha
        coluna = self.coluna
        inicio = self.pos
        while not self._fim() and (
            self._atual() in _LETRA or self._atual() in _DIGITO
        ):
            self._avancar()
        valor = self.codigo[inicio:self.pos]
        normalizado = valor.lower()
        if normalizado in PALAVRAS_CHAVE:
            return Token(PALAVRAS_CHAVE[normalizado], normalizado, linha, coluna)
        return Token(TokenType.IDENT, valor, linha, coluna)

    def _ler_operador(self):
        linha = self.linha
        coluna = self.coluna
        candidato_3 = self.codigo[self.pos:self.pos + 3]
        if candidato_3 in _OPERADORES_3CHAR:
            self._avancar()
            self._avancar()
            self._avancar()
            return Token(_OPERADORES_3CHAR[candidato_3], candidato_3, linha, coluna)
        candidato_2 = self.codigo[self.pos:self.pos + 2]
        if candidato_2 in _OPERADORES_2CHAR:
            self._avancar()
            self._avancar()
            return Token(_OPERADORES_2CHAR[candidato_2], candidato_2, linha, coluna)
        caractere = self._atual()
        if caractere in _OPERADORES_1CHAR:
            self._avancar()
            return Token(_OPERADORES_1CHAR[caractere], caractere, linha, coluna)
        if caractere in _PONTUACAO:
            self._avancar()
            return Token(_PONTUACAO[caractere], caractere, linha, coluna)
        raise ErroLexico(
            linha, coluna, f"caractere ilegal {caractere!r}"
        )

    def tokenize(self):
        """Produz a lista de tokens terminada em EOF (FR-001, FR-014)."""
        tokens = []
        while True:
            self._pular_espacos()
            if self._fim():
                break
            caractere = self._atual()
            if caractere in _DIGITO:
                tokens.append(self._ler_numero())
            elif caractere == '"':
                tokens.append(self._ler_cadeia())
            elif caractere in _LETRA:
                tokens.append(self._ler_identificador())
            else:
                tokens.append(self._ler_operador())
        tokens.append(Token(TokenType.EOF, "", self.linha, self.coluna))
        return tokens


def tokenize(codigo):
    """Conveniencia: tokeniza `codigo` via Lexer (FR-001)."""
    return Lexer(codigo).tokenize()
