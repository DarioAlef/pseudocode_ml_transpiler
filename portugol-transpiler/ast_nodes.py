"""Nos da AST do transpilador Portugol -> Python.

Responsabilidade: definir as estruturas de dados que representam os nos da
arvore sintatica abstrata do subset Portugol Studio. Estas classes sao
estruturas puras sem logica de parsing ou emissao de codigo: sao produzidas
pelo parser (etapa seguinte) e percorridas pelo emissor.

Todas as classes concretas herdam de Node, que centraliza o campo opcional
de posicao de origem (pos) e garante isinstance-check uniforme. O mecanismo
@dataclass fornece __init__, __eq__ e __repr__ legiveis automaticamente.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Position:
    """Localizacao no codigo-fonte original (linha/coluna 1-based, arquivo)."""

    linha: int = 0
    coluna: int = 0
    arquivo: str = ""


@dataclass
class Node:
    """Ancestral comum de todos os nos da AST.

    O campo pos e keyword-only para que os campos proprios de cada subclasse
    ocupem as posicoes posicionais do __init__, conforme os defaults do
    data-model. O __repr__ e __eq__ sao fornecidos pelo dataclass.
    """

    pos: Optional[Position] = field(default=None, kw_only=True)


@dataclass
class TypeNode(Node):
    """Tipo declarado: escalar ('inteiro'/'real'/'logico'/'cadeia') ou vetor/matriz."""

    base: str = ""
    is_array: bool = False
    dims: Optional[list] = None


@dataclass
class ParamNode(Node):
    """Parametro formal de funcao ou procedimento."""

    tipo: Optional[TypeNode] = None
    nome: str = ""
    is_ref: bool = False


@dataclass
class VarDeclNode(Node):
    """Declaracao de variavel local ou global."""

    tipo: Optional[TypeNode] = None
    nome: str = ""
    init: Optional[Node] = None
    is_ref: bool = False


@dataclass
class LiteralNode(Node):
    """Valor literal: inteiro, real, logico ou cadeia."""

    kind: str = ""
    value: Any = None


@dataclass
class BinaryExprNode(Node):
    """Expressao binaria: op aplicado a left e right."""

    op: str = ""
    left: Optional[Node] = None
    right: Optional[Node] = None


@dataclass
class UnaryExprNode(Node):
    """Expressao unaria: op aplicado a operand."""

    op: str = ""
    operand: Optional[Node] = None


@dataclass
class CallExprNode(Node):
    """Chamada de funcao ou procedimento."""

    callee: Optional[Any] = None
    args: list = field(default_factory=list)


@dataclass
class IndexExprNode(Node):
    """Acesso indexado: base[indices[0]] ou base[indices[0]][indices[1]]."""

    base: Optional[Node] = None
    indices: list = field(default_factory=list)


@dataclass
class AssignNode(Node):
    """Comando de atribuicao: alvo op valor."""

    alvo: Optional[Node] = None
    op: str = "="
    valor: Optional[Node] = None


@dataclass
class ReturnStmtNode(Node):
    """Comando retorne com valor opcional."""

    value: Optional[Node] = None


@dataclass
class BlockNode(Node):
    """Bloco de comandos sequenciais."""

    stmts: list = field(default_factory=list)


@dataclass
class IfStmtNode(Node):
    """Condicional se/senao se/senao.

    elifs e uma lista de pares (cond, BlockNode) representando cada 'senao se'.
    """

    cond: Optional[Node] = None
    then: Optional[BlockNode] = None
    elifs: list = field(default_factory=list)
    else_: Optional[BlockNode] = None


@dataclass
class ForStmtNode(Node):
    """Laco para com clausulas opcionais de init, cond e post."""

    init: Optional[Node] = None
    cond: Optional[Node] = None
    post: Optional[Node] = None
    body: Optional[BlockNode] = None


@dataclass
class WhileStmtNode(Node):
    """Laco enquanto."""

    cond: Optional[Node] = None
    body: Optional[BlockNode] = None


@dataclass
class FunctionNode(Node):
    """Funcao ou procedimento (tipo_retorno=None indica procedimento)."""

    nome: str = ""
    tipo_retorno: Optional[TypeNode] = None
    params: list = field(default_factory=list)
    body: Optional[BlockNode] = None


@dataclass
class ProgramNode(Node):
    """Raiz da AST: programa completo com funcoes e variaveis globais."""

    funcoes: list = field(default_factory=list)
    globais: list = field(default_factory=list)
    dialeto: str = "portugol_studio"
