"""Parser do transpilador Portugol -> Python.

Responsabilidade: consumir a lista de tokens produzida pelo lexer e montar
a AST (arvore sintatica abstrata) do programa usando os nos definidos em
ast_nodes.py. Implementa um parser descendente recursivo com subida de
precedencia para expressoes.
"""

from ast_nodes import (
    AssignNode,
    BinaryExprNode,
    BlockNode,
    CallExprNode,
    ForStmtNode,
    FunctionNode,
    IfStmtNode,
    IndexExprNode,
    LiteralNode,
    ParamNode,
    Position,
    ProgramNode,
    ReturnStmtNode,
    TypeNode,
    UnaryExprNode,
    VarDeclNode,
    WhileStmtNode,
)
from lexer import TokenType

_TIPOS = (TokenType.INTEIRO, TokenType.REAL, TokenType.LOGICO, TokenType.CADEIA)
_TIPO_NOMES = {
    TokenType.INTEIRO: "inteiro",
    TokenType.REAL: "real",
    TokenType.LOGICO: "logico",
    TokenType.CADEIA: "cadeia",
}


class ErroSintatico(Exception):
    """Erro de analise sintatica com localizacao (FR-018).

    Espelha ErroLexico: carrega linha/coluna do token ofensor e uma
    mensagem descritiva no formato 'esperado X, encontrado Y'.
    """

    def __init__(self, linha, coluna, mensagem):
        self.linha = linha
        self.coluna = coluna
        self.mensagem = mensagem
        super().__init__(
            f"Erro sintatico na linha {linha}, coluna {coluna}: {mensagem}"
        )


class Parser:
    """Parser descendente recursivo para o subset Portugol Studio.

    Consome list[Token] terminada em EOF e produz ProgramNode.
    Lanca ErroSintatico no primeiro desvio gramatical encontrado.
    """

    def __init__(self, tokens):
        """Inicializa o parser com a lista de tokens do lexer."""
        self._tokens = tokens
        self._pos = 0

    def _atual(self):
        return self._tokens[self._pos]

    def _avancar(self):
        token = self._tokens[self._pos]
        if self._pos < len(self._tokens) - 1:
            self._pos += 1
        return token

    def _verificar(self, *tipos):
        return self._atual().tipo in tipos

    def _casar(self, *tipos):
        if self._verificar(*tipos):
            return self._avancar()
        return None

    def _esperar(self, tipo, descricao=None):
        """Consome o token esperado ou lanca ErroSintatico com posicao."""
        if self._verificar(tipo):
            return self._avancar()
        token = self._atual()
        esperado = descricao or tipo.value
        raise ErroSintatico(
            token.linha,
            token.coluna,
            f"esperado '{esperado}', encontrado '{token.valor}'",
        )

    def _esperar_nome(self):
        """Aceita IDENT ou INICIO como nome (funcao inicio e keyword)."""
        if self._verificar(TokenType.IDENT, TokenType.INICIO):
            return self._avancar()
        token = self._atual()
        raise ErroSintatico(
            token.linha, token.coluna,
            f"nome esperado, encontrado '{token.valor}'"
        )

    def _pos_token(self, token=None):
        t = token or self._atual()
        return Position(t.linha, t.coluna)

    def parse(self):
        """Parseia o fluxo de tokens e retorna ProgramNode (FR-001).

        Lanca ErroSintatico se houver tokens apos o programa (FR-019).
        """
        ast = self._programa()
        if not self._verificar(TokenType.EOF):
            token = self._atual()
            raise ErroSintatico(
                token.linha,
                token.coluna,
                f"tokens inesperados apos o programa: '{token.valor}'",
            )
        return ast

    def _programa(self):
        pos = self._pos_token()
        self._esperar(TokenType.PROGRAMA, "programa")
        self._esperar(TokenType.LBRACE, "{")
        funcoes = []
        globais = []
        while not self._verificar(TokenType.RBRACE, TokenType.EOF):
            if self._verificar(TokenType.FUNCAO):
                funcoes.append(self._funcao())
            else:
                globais.append(self._var_decl())
        self._esperar(TokenType.RBRACE, "}")
        return ProgramNode(
            funcoes=funcoes, globais=globais, dialeto="portugol_studio", pos=pos
        )

    def _funcao(self):
        pos = self._pos_token()
        self._esperar(TokenType.FUNCAO, "funcao")
        tipo_retorno = None
        if self._verificar(*_TIPOS):
            tipo_retorno = self._tipo()
        nome_token = self._esperar_nome()
        nome = nome_token.valor
        self._esperar(TokenType.LPAREN, "(")
        params = []
        if not self._verificar(TokenType.RPAREN):
            params = self._params()
        self._esperar(TokenType.RPAREN, ")")
        body = self._bloco()
        return FunctionNode(
            nome=nome, tipo_retorno=tipo_retorno, params=params, body=body, pos=pos
        )

    def _params(self):
        params = [self._param()]
        while self._casar(TokenType.VIRGULA):
            params.append(self._param())
        return params

    def _param(self):
        pos = self._pos_token()
        is_ref = bool(self._casar(TokenType.AMP))
        tipo = self._tipo()
        nome_token = self._esperar(TokenType.IDENT, "nome do parametro")
        nome = nome_token.valor
        while self._casar(TokenType.LBRACKET):
            self._esperar(TokenType.RBRACKET, "]")
            tipo.is_array = True
            if tipo.dims is None:
                tipo.dims = []
        return ParamNode(tipo=tipo, nome=nome, is_ref=is_ref, pos=pos)

    def _tipo(self):
        pos = self._pos_token()
        token = self._atual()
        if token.tipo not in _TIPO_NOMES:
            raise ErroSintatico(
                token.linha, token.coluna,
                f"tipo esperado, encontrado '{token.valor}'"
            )
        self._avancar()
        return TypeNode(base=_TIPO_NOMES[token.tipo], is_array=False, dims=None, pos=pos)

    def _bloco(self):
        pos = self._pos_token()
        self._esperar(TokenType.LBRACE, "{")
        stmts = []
        while not self._verificar(TokenType.RBRACE, TokenType.EOF):
            stmts.append(self._statement())
        self._esperar(TokenType.RBRACE, "}")
        return BlockNode(stmts=stmts, pos=pos)

    def _statement(self):
        if self._verificar(*_TIPOS):
            return self._var_decl()
        if self._verificar(TokenType.SE):
            return self._se()
        if self._verificar(TokenType.ENQUANTO):
            return self._enquanto()
        if self._verificar(TokenType.PARA):
            return self._para()
        if self._verificar(TokenType.RETORNE):
            return self._retorne()
        return self._atribuicao_ou_chamada()

    def _var_decl(self):
        pos = self._pos_token()
        tipo = self._tipo()
        nome_token = self._esperar(TokenType.IDENT, "nome de variavel")
        nome = nome_token.valor
        if self._verificar(TokenType.LBRACKET):
            dims = []
            while self._casar(TokenType.LBRACKET):
                dims.append(self._expr())
                self._esperar(TokenType.RBRACKET, "]")
            tipo.is_array = True
            tipo.dims = dims
        init = None
        if self._casar(TokenType.ASSIGN):
            init = self._expr()
        return VarDeclNode(tipo=tipo, nome=nome, init=init, pos=pos)

    def _atribuicao_ou_chamada(self):
        pos = self._pos_token()
        nome_token = self._esperar_nome()
        nome = nome_token.valor
        if self._verificar(TokenType.LPAREN):
            return self._chamada(nome, pos)
        indices = []
        while self._verificar(TokenType.LBRACKET):
            self._avancar()
            indices.append(self._expr())
            self._esperar(TokenType.RBRACKET, "]")
        alvo_base = LiteralNode(kind="ident", value=nome, pos=pos)
        alvo = (
            IndexExprNode(base=alvo_base, indices=indices, pos=pos)
            if indices
            else alvo_base
        )
        if self._verificar(TokenType.INC):
            self._avancar()
            one = LiteralNode(kind="int", value="1")
            return AssignNode(
                alvo=alvo, op="=",
                valor=BinaryExprNode(op="+", left=alvo, right=one),
                pos=pos,
            )
        if self._verificar(TokenType.DEC):
            self._avancar()
            one = LiteralNode(kind="int", value="1")
            return AssignNode(
                alvo=alvo, op="=",
                valor=BinaryExprNode(op="-", left=alvo, right=one),
                pos=pos,
            )
        self._esperar(TokenType.ASSIGN, "=")
        valor = self._expr()
        return AssignNode(alvo=alvo, op="=", valor=valor, pos=pos)

    def _chamada(self, nome, pos):
        """Parseia lista de argumentos e retorna CallExprNode."""
        self._esperar(TokenType.LPAREN, "(")
        args = []
        if not self._verificar(TokenType.RPAREN):
            args.append(self._expr())
            while self._casar(TokenType.VIRGULA):
                args.append(self._expr())
        self._esperar(TokenType.RPAREN, ")")
        callee = LiteralNode(kind="ident", value=nome, pos=pos)
        return CallExprNode(callee=callee, args=args, pos=pos)

    def _se(self):
        pos = self._pos_token()
        self._esperar(TokenType.SE, "se")
        self._esperar(TokenType.LPAREN, "(")
        cond = self._expr()
        self._esperar(TokenType.RPAREN, ")")
        then = self._bloco()
        elifs = []
        else_ = None
        while self._verificar(TokenType.SENAO):
            self._avancar()
            if self._verificar(TokenType.SE):
                self._avancar()
                self._esperar(TokenType.LPAREN, "(")
                elif_cond = self._expr()
                self._esperar(TokenType.RPAREN, ")")
                elif_body = self._bloco()
                elifs.append((elif_cond, elif_body))
            else:
                else_ = self._bloco()
                break
        return IfStmtNode(cond=cond, then=then, elifs=elifs, else_=else_, pos=pos)

    def _enquanto(self):
        pos = self._pos_token()
        self._esperar(TokenType.ENQUANTO, "enquanto")
        self._esperar(TokenType.LPAREN, "(")
        cond = self._expr()
        self._esperar(TokenType.RPAREN, ")")
        body = self._bloco()
        return WhileStmtNode(cond=cond, body=body, pos=pos)

    def _para(self):
        pos = self._pos_token()
        self._esperar(TokenType.PARA, "para")
        self._esperar(TokenType.LPAREN, "(")
        init = None
        if not self._verificar(TokenType.PONTO_VIRGULA):
            if self._verificar(*_TIPOS):
                init = self._var_decl()
            else:
                init = self._atribuicao_ou_chamada()
        self._esperar(TokenType.PONTO_VIRGULA, ";")
        cond = None
        if not self._verificar(TokenType.PONTO_VIRGULA):
            cond = self._expr()
        self._esperar(TokenType.PONTO_VIRGULA, ";")
        post = None
        if not self._verificar(TokenType.RPAREN):
            post = self._post_para()
        self._esperar(TokenType.RPAREN, ")")
        body = self._bloco()
        return ForStmtNode(init=init, cond=cond, post=post, body=body, pos=pos)

    def _post_para(self):
        """Parseia a parte post do para: atribuicao ou i++/i--."""
        pos = self._pos_token()
        nome_token = self._esperar_nome()
        nome = nome_token.valor
        alvo = LiteralNode(kind="ident", value=nome, pos=pos)
        if self._verificar(TokenType.INC):
            self._avancar()
            one = LiteralNode(kind="int", value="1")
            return AssignNode(
                alvo=alvo, op="=",
                valor=BinaryExprNode(op="+", left=alvo, right=one),
                pos=pos,
            )
        if self._verificar(TokenType.DEC):
            self._avancar()
            one = LiteralNode(kind="int", value="1")
            return AssignNode(
                alvo=alvo, op="=",
                valor=BinaryExprNode(op="-", left=alvo, right=one),
                pos=pos,
            )
        self._esperar(TokenType.ASSIGN, "=")
        valor = self._expr()
        return AssignNode(alvo=alvo, op="=", valor=valor, pos=pos)

    def _retorne(self):
        pos = self._pos_token()
        self._esperar(TokenType.RETORNE, "retorne")
        value = None
        if not self._verificar(TokenType.RBRACE, TokenType.EOF, TokenType.PONTO_VIRGULA):
            value = self._expr()
        return ReturnStmtNode(value=value, pos=pos)

    def _expr(self):
        return self._ou()

    def _ou(self):
        left = self._e()
        while self._verificar(TokenType.OR):
            op = self._avancar().valor
            right = self._e()
            left = BinaryExprNode(op=op, left=left, right=right)
        return left

    def _e(self):
        left = self._igualdade()
        while self._verificar(TokenType.AND):
            op = self._avancar().valor
            right = self._igualdade()
            left = BinaryExprNode(op=op, left=left, right=right)
        return left

    def _igualdade(self):
        left = self._comparacao()
        while self._verificar(TokenType.EQ, TokenType.NEQ):
            op = self._avancar().valor
            right = self._comparacao()
            left = BinaryExprNode(op=op, left=left, right=right)
        return left

    def _comparacao(self):
        left = self._adicao()
        while self._verificar(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op = self._avancar().valor
            right = self._adicao()
            left = BinaryExprNode(op=op, left=left, right=right)
        return left

    def _adicao(self):
        left = self._multiplicacao()
        while self._verificar(TokenType.MAIS, TokenType.MENOS):
            op = self._avancar().valor
            right = self._multiplicacao()
            left = BinaryExprNode(op=op, left=left, right=right)
        return left

    def _multiplicacao(self):
        left = self._unario()
        while self._verificar(TokenType.MULT, TokenType.DIV, TokenType.MOD):
            op = self._avancar().valor
            right = self._unario()
            left = BinaryExprNode(op=op, left=left, right=right)
        return left

    def _unario(self):
        if self._verificar(TokenType.MENOS):
            op = self._avancar().valor
            return UnaryExprNode(op=op, operand=self._unario())
        if self._verificar(TokenType.NOT):
            op = self._avancar().valor
            return UnaryExprNode(op=op, operand=self._unario())
        return self._potencia()

    def _potencia(self):
        base = self._primario()
        if self._verificar(TokenType.POT):
            op = self._avancar().valor
            return BinaryExprNode(op=op, left=base, right=self._unario())
        return base

    def _primario(self):
        pos = self._pos_token()
        token = self._atual()
        if token.tipo == TokenType.INT_LIT:
            self._avancar()
            return LiteralNode(kind="int", value=token.valor, pos=pos)
        if token.tipo == TokenType.FLOAT_LIT:
            self._avancar()
            return LiteralNode(kind="real", value=token.valor, pos=pos)
        if token.tipo == TokenType.STRING_LIT:
            self._avancar()
            return LiteralNode(kind="cadeia", value=token.valor, pos=pos)
        if token.tipo == TokenType.BOOL_LIT:
            self._avancar()
            return LiteralNode(kind="logico", value=token.valor, pos=pos)
        if token.tipo == TokenType.LPAREN:
            self._avancar()
            expr = self._expr()
            self._esperar(TokenType.RPAREN, ")")
            return expr
        if token.tipo in (TokenType.IDENT, TokenType.INICIO):
            self._avancar()
            nome = token.valor
            if self._verificar(TokenType.LPAREN):
                return self._chamada(nome, pos)
            if self._verificar(TokenType.LBRACKET):
                indices = []
                while self._verificar(TokenType.LBRACKET):
                    self._avancar()
                    indices.append(self._expr())
                    self._esperar(TokenType.RBRACKET, "]")
                base = LiteralNode(kind="ident", value=nome, pos=pos)
                return IndexExprNode(base=base, indices=indices, pos=pos)
            return LiteralNode(kind="ident", value=nome, pos=pos)
        raise ErroSintatico(
            token.linha,
            token.coluna,
            f"expressao esperada, encontrado '{token.valor}'",
        )


def parse(tokens):
    """Conveniencia: parseia tokens via Parser (FR-001)."""
    return Parser(tokens).parse()
