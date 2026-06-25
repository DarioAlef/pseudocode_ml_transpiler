"""Analise semantica minima do transpilador Portugol -> Python.

Responsabilidade: percorrer a AST (produzida por parser.parse), popular uma
tabela de simbolos com escopos aninhados e acumular diagnosticos (avisos e
erros) sem nunca abortar. E um estagio opcional entre parser e emissor: a CLI
executa `analisar`, reporta os diagnosticos e passa a `SymbolTable` ao emissor
para resolver tipos em `leia` (Cards 12 e 13).

Contrato publico:
  - dataclasses Symbol, Diagnostico, SymbolTable
  - classe Scope (declarar/resolver) e classe SemanticAnalyzer
  - funcao de conveniencia analisar(programa) -> (SymbolTable, list[Diagnostico])

Diagnosticos cobertos:
  - variavel usada sem declaracao no escopo acessivel -> aviso (FR-013)
  - funcao declarada chamada com aridade errada -> erro nao-fatal (FR-014)
  - retorno com valor em procedimento -> aviso (FR-015)
"""

from dataclasses import dataclass, field
from typing import Optional

from ast_nodes import (
    AssignNode,
    BinaryExprNode,
    BlockNode,
    CallExprNode,
    ForStmtNode,
    IfStmtNode,
    IndexExprNode,
    LiteralNode,
    ReturnStmtNode,
    UnaryExprNode,
    VarDeclNode,
    WhileStmtNode,
)

_BUILTINS = {
    "escreva",
    "escreval",
    "leia",
    "exp",
    "logaritmo",
    "raiz",
    "potencia",
    "seno",
    "cosseno",
    "piso",
    "teto",
    "absoluto",
    "arredondar",
    "minimo",
    "maximo",
    "aleatorio",
    "ler_csv",
    "normalizar_zscore",
    "dividir_treino_teste",
    "salvar_pesos",
    "carregar_pesos",
}


@dataclass
class Symbol:
    """Nome declarado: variavel, funcao ou parametro."""

    nome: str
    tipo: str = ""
    kind: str = "var"
    is_ref: bool = False
    is_array: bool = False
    aridade: Optional[int] = None


class Scope:
    """Container de simbolos com encadeamento ao escopo pai."""

    def __init__(self, parent=None):
        """Inicializa um escopo vazio com referencia opcional ao pai."""
        self.symbols = {}
        self.parent = parent

    def declarar(self, symbol):
        """Registra um simbolo neste escopo (ultima declaracao prevalece)."""
        self.symbols[symbol.nome] = symbol

    def resolver(self, nome):
        """Procura o nome neste escopo e nos ancestrais; None se ausente."""
        escopo = self
        while escopo is not None:
            if nome in escopo.symbols:
                return escopo.symbols[nome]
            escopo = escopo.parent
        return None


@dataclass
class Diagnostico:
    """Mensagem da analise semantica com severidade e localizacao."""

    severidade: str
    mensagem: str
    linha: int
    coluna: int


@dataclass
class SymbolTable:
    """Tabela de consulta exposta ao emissor (escopo global + por funcao)."""

    global_scope: Scope
    escopos_por_funcao: dict = field(default_factory=dict)

    def tipo_de(self, nome, escopo_funcao=None):
        """Resolve o tipo base de `nome`, do escopo da funcao ate o global.

        Devolve None quando o nome nao existe ou nao tem tipo conhecido.
        """
        if escopo_funcao is not None and escopo_funcao in self.escopos_por_funcao:
            simbolo = self.escopos_por_funcao[escopo_funcao].resolver(nome)
            if simbolo is not None:
                return simbolo.tipo or None
        simbolo = self.global_scope.resolver(nome)
        if simbolo is not None:
            return simbolo.tipo or None
        return None


class SemanticAnalyzer:
    """Percorre a AST, popula escopos e acumula diagnosticos (nao-fatal)."""

    def __init__(self):
        """Inicializa o estado: escopo global, mapa por funcao e diagnosticos."""
        self.global_scope = Scope()
        self.escopos_por_funcao = {}
        self.diagnosticos = []
        self._em_procedimento = False

    def analisar(self, programa):
        """Analisa o programa e devolve (SymbolTable, list[Diagnostico])."""
        for decl in programa.globais:
            self._declarar_var(decl, self.global_scope)
        for func in programa.funcoes:
            tipo = func.tipo_retorno.base if func.tipo_retorno is not None else ""
            self.global_scope.declarar(
                Symbol(nome=func.nome, tipo=tipo, kind="func", aridade=len(func.params))
            )
        for func in programa.funcoes:
            self._analisar_funcao(func)
        tabela = SymbolTable(self.global_scope, self.escopos_por_funcao)
        return tabela, self.diagnosticos

    def _analisar_funcao(self, func):
        """Cria o escopo da funcao, declara parametros e visita o corpo."""
        escopo = Scope(parent=self.global_scope)
        for param in func.params:
            tipo = param.tipo.base if param.tipo is not None else ""
            is_array = bool(param.tipo.is_array) if param.tipo is not None else False
            escopo.declarar(
                Symbol(
                    nome=param.nome, tipo=tipo, kind="param",
                    is_ref=param.is_ref, is_array=is_array,
                )
            )
        self.escopos_por_funcao[func.nome] = escopo
        anterior = self._em_procedimento
        self._em_procedimento = func.tipo_retorno is None
        if func.body is not None:
            self._visitar_bloco(func.body, escopo)
        self._em_procedimento = anterior

    def _declarar_var(self, decl, escopo):
        """Registra um VarDeclNode no escopo informado."""
        tipo = decl.tipo.base if decl.tipo is not None else ""
        is_array = bool(decl.tipo.is_array) if decl.tipo is not None else False
        escopo.declarar(
            Symbol(nome=decl.nome, tipo=tipo, kind="var", is_array=is_array)
        )

    def _visitar_bloco(self, bloco, escopo):
        """Visita sequencialmente os statements de um BlockNode."""
        for stmt in bloco.stmts:
            self._visitar_stmt(stmt, escopo)

    def _visitar_stmt(self, node, escopo):
        """Despacha um statement para a visita especifica por tipo."""
        if isinstance(node, VarDeclNode):
            if node.tipo is not None and node.tipo.dims:
                for dim in node.tipo.dims:
                    self._visitar_expr(dim, escopo)
            if node.init is not None:
                self._visitar_expr(node.init, escopo)
            self._declarar_var(node, escopo)
        elif isinstance(node, AssignNode):
            self._visitar_assign(node, escopo)
        elif isinstance(node, IfStmtNode):
            self._visitar_expr(node.cond, escopo)
            self._visitar_bloco(node.then, escopo)
            for cond, corpo in node.elifs:
                self._visitar_expr(cond, escopo)
                self._visitar_bloco(corpo, escopo)
            if node.else_ is not None:
                self._visitar_bloco(node.else_, escopo)
        elif isinstance(node, WhileStmtNode):
            self._visitar_expr(node.cond, escopo)
            self._visitar_bloco(node.body, escopo)
        elif isinstance(node, ForStmtNode):
            if node.init is not None:
                self._visitar_stmt(node.init, escopo)
            if node.cond is not None:
                self._visitar_expr(node.cond, escopo)
            if node.post is not None:
                self._visitar_stmt(node.post, escopo)
            self._visitar_bloco(node.body, escopo)
        elif isinstance(node, ReturnStmtNode):
            if node.value is not None:
                self._visitar_expr(node.value, escopo)
                if self._em_procedimento:
                    self._aviso(node, "retorno com valor em procedimento")
        elif isinstance(node, CallExprNode):
            self._visitar_call(node, escopo)
        elif isinstance(node, BlockNode):
            self._visitar_bloco(node, escopo)

    def _visitar_assign(self, node, escopo):
        """Visita o valor (uso) e registra o alvo ident como declarado."""
        if node.valor is not None:
            self._visitar_expr(node.valor, escopo)
        alvo = node.alvo
        if isinstance(alvo, IndexExprNode):
            self._visitar_expr(alvo, escopo)
        elif isinstance(alvo, LiteralNode) and alvo.kind == "ident":
            if escopo.resolver(alvo.value) is None and alvo.value not in _BUILTINS:
                escopo.declarar(Symbol(nome=alvo.value, tipo="", kind="var"))

    def _visitar_expr(self, node, escopo):
        """Visita uma expressao registrando usos de identificadores."""
        if isinstance(node, LiteralNode):
            if node.kind == "ident":
                if escopo.resolver(node.value) is None and node.value not in _BUILTINS:
                    self._aviso(node, f"variavel '{node.value}' usada sem declaracao")
        elif isinstance(node, BinaryExprNode):
            self._visitar_expr(node.left, escopo)
            self._visitar_expr(node.right, escopo)
        elif isinstance(node, UnaryExprNode):
            self._visitar_expr(node.operand, escopo)
        elif isinstance(node, CallExprNode):
            self._visitar_call(node, escopo)
        elif isinstance(node, IndexExprNode):
            self._visitar_expr(node.base, escopo)
            for indice in node.indices:
                self._visitar_expr(indice, escopo)

    def _visitar_call(self, node, escopo):
        """Verifica aridade de funcao declarada e visita os argumentos."""
        callee = node.callee
        nome = None
        if isinstance(callee, LiteralNode) and callee.kind == "ident":
            nome = callee.value
        if nome is not None and nome not in _BUILTINS:
            simbolo = self.global_scope.resolver(nome)
            if (
                simbolo is not None
                and simbolo.kind == "func"
                and simbolo.aridade is not None
                and len(node.args) != simbolo.aridade
            ):
                self._erro(
                    node,
                    f"funcao '{nome}' chamada com {len(node.args)} argumento(s), "
                    f"esperados {simbolo.aridade}",
                )
        for arg in node.args:
            self._visitar_expr(arg, escopo)

    def _aviso(self, node, mensagem):
        """Acumula um diagnostico de severidade 'aviso' na posicao do no."""
        linha, coluna = self._posicao(node)
        self.diagnosticos.append(Diagnostico("aviso", mensagem, linha, coluna))

    def _erro(self, node, mensagem):
        """Acumula um diagnostico de severidade 'erro' (nao-fatal)."""
        linha, coluna = self._posicao(node)
        self.diagnosticos.append(Diagnostico("erro", mensagem, linha, coluna))

    def _posicao(self, node):
        """Extrai (linha, coluna) do no, ou (0, 0) quando ausente."""
        if node.pos is not None:
            return node.pos.linha, node.pos.coluna
        return 0, 0


def analisar(programa):
    """Atalho equivalente a SemanticAnalyzer().analisar(programa)."""
    return SemanticAnalyzer().analisar(programa)
