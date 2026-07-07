"""Emissor de codigo Python do transpilador Portugol -> Python.

Responsabilidade: percorrer a AST (produzida por parser.parse) e gerar uma
string de codigo Python equivalente, com controle de indentacao, mapas de
operadores/zero-values/builtins e imports seletivos. Nao realiza I/O: devolve
a string em memoria. A CLI (transpilador.py) e responsavel por escrever o
arquivo .py e copiar o runtime.

Contrato publico:
  - classe Emissor com metodo gerar(programa: ProgramNode) -> str
  - funcao de conveniencia emitir(programa) -> str
Garantias sobre a string retornada:
  1. Primeira linha == "# GERADO AUTOMATICAMENTE"
  2. Resultado passa em compile(...) / python -m py_compile
  3. Indentacao somente com espacos, em multiplos de 4
  4. Rodape "if __name__ == \"__main__\":\\n    inicio()"
  5. Imports presentes <-> builtin correspondente usado (seletividade)
"""

from ast_nodes import (
    AssignNode,
    BinaryExprNode,
    BlockNode,
    BreakNode,
    CallExprNode,
    EscolhaCasoNode,
    ForStmtNode,
    IfStmtNode,
    IncluaNode,
    IndexExprNode,
    LiteralNode,
    MemberAccessNode,
    ReturnStmtNode,
    UnaryExprNode,
    VarDeclNode,
    WhileStmtNode,
)

_CABECALHO = "# GERADO AUTOMATICAMENTE"

_ZERO_VALUES = {
    "inteiro": "0",
    "real": "0.0",
    "logico": "False",
    "cadeia": "\"\"",
}

_OPERADORES_BIN = {
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "%": "%",
    "^": "**",
    "<": "<",
    ">": ">",
    "<=": "<=",
    ">=": ">=",
    "==": "==",
    "!=": "!=",
    "e": "and",
    "ou": "or",
    "&&": "and",
    "||": "or",
}

_OPERADORES_UN = {
    "-": "-",
    "nao": "not",
    "!": "not",
}

_BUILTINS_MATH = {
    "exp": "math.exp",
    "logaritmo": "math.log",
    "raiz": "math.sqrt",
    "potencia": "math.pow",
    "seno": "math.sin",
    "cosseno": "math.cos",
    "piso": "math.floor",
    "teto": "math.ceil",
}

_BUILTINS_NATIVOS = {
    "absoluto": "abs",
    "arredondar": "round",
    "minimo": "min",
    "maximo": "max",
}

_BUILTINS_RUNTIME = {
    "ler_csv",
    "normalizar_zscore",
    "normalizar_treino_teste",
    "dividir_treino_teste",
    "salvar_pesos",
    "carregar_pesos",
    "plotar_previsoes",
    "plotar_dispersao",
    "recomendar_producao",
    "limpa",
    "arq",
    "tx",
    "ti",
}


class Emissor:
    """Percorre a AST e produz codigo Python em uma string.

    Estado mutavel durante uma geracao; reiniciado a cada chamada de gerar().
    Determinismo: mesma entrada produz sempre a mesma saida.
    """

    def __init__(self):
        """Inicializa o estado interno vazio (pronto para gerar)."""
        self._buffer = []
        self._nivel = 0
        self._globais_escalares = {}
        self._globais_compostas = set()
        self._locais = {}
        self._usou_math = False
        self._usou_random = False
        self._runtime_usado = set()
        self._tabela_simbolos = None
        self._funcao_atual = None
        self._innermost_block = []

    def gerar(self, programa, tabela_simbolos=None):
        """Gera o codigo Python completo a partir de um ProgramNode.

        Reinicia o estado a cada chamada (deterministico). Nao modifica o
        programa recebido. Retorna str terminado em newline.
        """
        self._buffer = []
        self._nivel = 0
        self._globais_escalares = {}
        self._globais_compostas = set()
        self._locais = {}
        self._usou_math = False
        self._usou_random = False
        self._runtime_usado = set()
        self._tabela_simbolos = tabela_simbolos
        self._funcao_atual = None
        self._innermost_block = []

        self._registrar_globais(programa.globais)

        for decl in programa.globais:
            self._emitir_stmt(decl)

        for func in programa.funcoes:
            self._emitir_funcao(func)

        self.linha("if __name__ == \"__main__\":")
        self.indentar()
        self.linha("inicio()")
        self.desindentar()

        corpo = "\n".join(self._buffer) + "\n"
        cabecalho = self._montar_cabecalho()
        return cabecalho + corpo

    def linha(self, texto):
        """Anexa uma linha ao buffer com a indentacao corrente (4 espacos/nivel)."""
        self._buffer.append("    " * self._nivel + texto)

    def indentar(self):
        """Incrementa um nivel de indentacao."""
        self._nivel += 1

    def desindentar(self):
        """Decrementa um nivel de indentacao."""
        if self._nivel > 0:
            self._nivel -= 1

    def _montar_cabecalho(self):
        """Monta o cabecalho seletivo: comentario + imports conforme uso."""
        linhas = [_CABECALHO]
        if self._usou_math:
            linhas.append("import math")
        if self._usou_random:
            linhas.append("import random")
        if self._runtime_usado:
            funcs = sorted(self._runtime_usado)
            linhas.append("from runtime_portugol import " + ", ".join(funcs))
        return "\n".join(linhas) + "\n"

    def _registrar_globais(self, globais):
        """Classifica globais em escalares (nome -> tipo base) e compostas (set)."""
        for decl in globais:
            if isinstance(decl, VarDeclNode) and decl.tipo is not None:
                if decl.tipo.is_array:
                    self._globais_compostas.add(decl.nome)
                else:
                    self._globais_escalares[decl.nome] = decl.tipo.base

    def _coletar_globais_reatribuidas(self, func):
        """Coleta nomes de globais escalares reatribuidos em func (AssignNode simples).

        Desconta parametros e VarDeclNode locais; ignora atribuicao indexada
        (mutacao de lista nao exige `global` em Python).
        """
        locais = set()
        for param in func.params:
            locais.add(param.nome)

        reatribuidos = set()

        def visitar(stmt):
            if isinstance(stmt, VarDeclNode):
                locais.add(stmt.nome)
                if stmt.init is not None:
                    visitar(stmt.init)
            elif isinstance(stmt, AssignNode):
                alvo = stmt.alvo
                if (
                    isinstance(alvo, LiteralNode)
                    and alvo.kind == "ident"
                ):
                    nome = alvo.value
                    if nome not in locais:
                        reatribuidos.add(nome)
                if stmt.valor is not None:
                    visitar(stmt.valor)
            elif isinstance(stmt, BlockNode):
                for s in stmt.stmts:
                    visitar(s)
            elif isinstance(stmt, IfStmtNode):
                if stmt.cond is not None:
                    visitar(stmt.cond)
                if stmt.then is not None:
                    visitar(stmt.then)
                for cond, corpo in stmt.elifs:
                    if cond is not None:
                        visitar(cond)
                    if corpo is not None:
                        visitar(corpo)
                if stmt.else_ is not None:
                    visitar(stmt.else_)
            elif isinstance(stmt, WhileStmtNode):
                if stmt.cond is not None:
                    visitar(stmt.cond)
                if stmt.body is not None:
                    visitar(stmt.body)
            elif isinstance(stmt, ForStmtNode):
                if stmt.init is not None:
                    visitar(stmt.init)
                if stmt.cond is not None:
                    visitar(stmt.cond)
                if stmt.post is not None:
                    visitar(stmt.post)
                if stmt.body is not None:
                    visitar(stmt.body)
            elif isinstance(stmt, ReturnStmtNode):
                if stmt.value is not None:
                    visitar(stmt.value)
            elif isinstance(stmt, (BinaryExprNode,)):
                if stmt.left is not None:
                    visitar(stmt.left)
                if stmt.right is not None:
                    visitar(stmt.right)
            elif isinstance(stmt, UnaryExprNode):
                if stmt.operand is not None:
                    visitar(stmt.operand)
            elif isinstance(stmt, CallExprNode):
                for a in stmt.args:
                    visitar(a)
            elif isinstance(stmt, IndexExprNode):
                if stmt.base is not None:
                    visitar(stmt.base)
                for i in stmt.indices:
                    visitar(i)

        if func.body is not None:
            visitar(func.body)

        return {
            nome for nome in reatribuidos
            if nome in self._globais_escalares and nome not in locais
        }

    def _emitir_bloco(self, block):
        """Emite um BlockNode: seus statements, ou `pass` se vazio (FR-020)."""
        if block is None or not block.stmts:
            self.linha("pass")
            return
        for stmt in block.stmts:
            self._emitir_stmt(stmt)

    def _emitir_stmt(self, node):
        """Despacha statement para o emissor especifico por tipo de no."""
        if isinstance(node, VarDeclNode):
            self._emitir_var_decl(node)
        elif isinstance(node, AssignNode):
            self._emitir_assign(node)
        elif isinstance(node, IfStmtNode):
            self._emitir_if(node)
        elif isinstance(node, WhileStmtNode):
            self._emitir_while(node)
        elif isinstance(node, ForStmtNode):
            self._emitir_for(node)
        elif isinstance(node, ReturnStmtNode):
            self._emitir_return(node)
        elif isinstance(node, CallExprNode):
            self._emitir_call_stmt(node)
        elif isinstance(node, BlockNode):
            self._emitir_bloco(node)
        elif isinstance(node, EscolhaCasoNode):
            self._emitir_escolha(node)
        elif isinstance(node, BreakNode):
            self._emitir_break(node)
        elif isinstance(node, IncluaNode):
            pass  # tratamos os imports nativamente
        else:
            raise NotImplementedError(
                f"statement nao suportado: {type(node).__name__}"
            )

    def _emitir_var_decl(self, node):
        """Emite declaracao de variavel: escalar, vetor ou matriz."""
        zero = _ZERO_VALUES.get(node.tipo.base, "0")
        nome = node.nome
        if node.tipo.is_array:
            dims = node.tipo.dims or []
            if len(dims) == 1:
                tam = self._expr(dims[0])
                if node.init is not None:
                    self.linha(f"{nome} = {self._expr(node.init)}")
                else:
                    self.linha(f"{nome} = [{zero}] * {tam}")
            else:
                if node.init is not None:
                    self.linha(f"{nome} = {self._expr(node.init)}")
                else:
                    linhas_dim = self._expr(dims[0])
                    cols_dim = self._expr(dims[1])
                    self.linha(
                        f"{nome} = [[{zero}] * {cols_dim} for _ in range({linhas_dim})]"
                    )
        else:
            self._locais[nome] = node.tipo.base
            if node.init is not None:
                self.linha(f"{nome} = {self._expr(node.init)}")
            else:
                self.linha(f"{nome} = {zero}")

    def _emitir_assign(self, node):
        """Emite atribuicao: alvo ident ou IndexExpr."""
        alvo = self._expr(node.alvo)
        valor = self._expr(node.valor)
        self.linha(f"{alvo} = {valor}")

    def _emitir_if(self, node):
        """Emite if / elif / else com indentacao por bloco."""
        cond = self._expr(node.cond)
        self.linha(f"if {cond}:")
        self.indentar()
        self._emitir_bloco(node.then)
        self.desindentar()
        for elif_cond, elif_body in node.elifs:
            c = self._expr(elif_cond)
            self.linha(f"elif {c}:")
            self.indentar()
            self._emitir_bloco(elif_body)
            self.desindentar()
        if node.else_ is not None:
            self.linha("else:")
            self.indentar()
            self._emitir_bloco(node.else_)
            self.desindentar()

    def _emitir_while(self, node):
        """Emite while cond: + corpo indentado."""
        cond = self._expr(node.cond)
        self.linha(f"while {cond}:")
        self.indentar()
        self._innermost_block.append("loop")
        self._emitir_bloco(node.body)
        self._innermost_block.pop()
        self.desindentar()

    def _emitir_for(self, node):
        """Emite ForStmt: range se padrao simples, senao while equivalente."""
        padrao = self._tentar_for_range(node)
        if padrao is not None:
            var, inicio, fim, passo = padrao
            if passo == 1:
                self.linha(f"for {var} in range({inicio}, {fim}):")
            elif passo == -1:
                self.linha(f"for {var} in range({inicio}, {fim}, -1):")
            else:
                self.linha(f"for {var} in range({inicio}, {fim}, {passo}):")
            self.indentar()
            self._innermost_block.append("loop")
            self._emitir_bloco(node.body)
            self._innermost_block.pop()
            self.desindentar()
            return

        if node.init is not None:
            self._emitir_stmt(node.init)
        cond = self._expr(node.cond) if node.cond is not None else "True"
        self.linha(f"while {cond}:")
        self.indentar()
        self._innermost_block.append("loop")
        self._emitir_bloco(node.body)
        self._innermost_block.pop()
        if node.post is not None:
            self._emitir_stmt(node.post)
        self.desindentar()

    def _tentar_for_range(self, node):
        """Tenta reconhecer o padrao simples de ForStmt -> (var, inicio, fim, passo).

        Retorna None se nao for o padrao. Padrão exige:
        - init: VarDeclNode(int) com init, ou AssignNode i = <expr>
        - cond: BinaryExprNode relacional com left == ident i
        - post: AssignNode i = i (+/-) k
        """
        init = node.init
        cond = node.cond
        post = node.post
        if init is None or cond is None or post is None:
            return None
        if not isinstance(cond, BinaryExprNode):
            return None
        if not isinstance(post, AssignNode):
            return None

        if isinstance(init, VarDeclNode):
            if init.tipo is None or init.tipo.base != "inteiro" or init.init is None:
                return None
            var = init.nome
            inicio = self._expr(init.init)
        elif isinstance(init, AssignNode):
            alvo = init.alvo
            if not (isinstance(alvo, LiteralNode) and alvo.kind == "ident"):
                return None
            var = alvo.value
            inicio = self._expr(init.valor)
        else:
            return None

        left = cond.left
        if not (isinstance(left, LiteralNode) and left.kind == "ident" and left.value == var):
            return None

        op = cond.op
        fim_expr = self._expr(cond.right)
        if op == "<":
            fim = fim_expr
        elif op == "<=":
            fim = fim_expr + " + 1"
        elif op == ">":
            fim = fim_expr
        elif op == ">=":
            fim = fim_expr + " - 1"
        else:
            return None

        post_alvo = post.alvo
        if not (
            isinstance(post_alvo, LiteralNode)
            and post_alvo.kind == "ident"
            and post_alvo.value == var
        ):
            return None
        if not isinstance(post.valor, BinaryExprNode):
            return None
        if post.valor.op == "+":
            right = post.valor.right
            if isinstance(right, LiteralNode) and right.kind == "int" and right.value == "1":
                passo = 1
            else:
                passo = self._expr(post.valor.right)
        elif post.valor.op == "-":
            right = post.valor.right
            if isinstance(right, LiteralNode) and right.kind == "int" and right.value == "1":
                passo = -1
            else:
                passo = "-" + self._expr(post.valor.right)
        else:
            return None

        if op in (">", ">=") and passo != -1:
            return None
        if op in ("<", "<=") and passo == -1:
            return None

        return var, inicio, fim, passo

    def _emitir_escolha(self, node):
        expr = self._expr(node.expr)
        self.linha(f"match {expr}:")
        self.indentar()
        self._innermost_block.append("escolha")
        for caso_expr, corpo in node.casos:
            val = self._expr(caso_expr)
            self.linha(f"case {val}:")
            self.indentar()
            self._emitir_bloco(corpo)
            self.desindentar()
        if node.caso_contrario is not None:
            self.linha("case _:")
            self.indentar()
            self._emitir_bloco(node.caso_contrario)
            self.desindentar()
        self._innermost_block.pop()
        self.desindentar()

    def _emitir_break(self, node):
        if self._innermost_block and self._innermost_block[-1] == "loop":
            self.linha("break")
        else:
            self.linha("pass  # pare (ignorado por restricoes do Python match)")

    def _emitir_return(self, node):
        """Emite return <expr> ou return."""
        if node.value is not None:
            self.linha(f"return {self._expr(node.value)}")
        else:
            self.linha("return")

    def _emitir_call_stmt(self, node):
        """Emite chamada usada como statement.

        `leia` recebe tratamento especial: emite uma linha de leitura por
        argumento (FR-021), cada uma com a conversao do seu tipo.
        """
        callee = node.callee
        if isinstance(callee, LiteralNode) and callee.kind == "ident" and callee.value == "leia":
            if not node.args:
                self.linha("input()")
                return
            for arg in node.args:
                self.linha(self._leia_linha(arg))
            return
        self.linha(self._expr(node))

    def _emitir_funcao(self, func):
        """Emite def nome(params): + global + corpo (ou pass)."""
        self._locais = {}
        self._funcao_atual = func.nome
        for param in func.params:
            if param.tipo is not None:
                self._locais[param.nome] = param.tipo.base
            else:
                self._locais[param.nome] = ""

        params_str = ", ".join(p.nome for p in func.params)
        self.linha(f"def {func.nome}({params_str}):")
        self.indentar()

        reatribuidos = self._coletar_globais_reatribuidas(func)
        for nome in sorted(reatribuidos):
            self.linha(f"global {nome}")

        self._emitir_bloco(func.body)
        self.desindentar()
        self.linha("")
        self._funcao_atual = None

    def _expr(self, node):
        """Despacha expressao para o emissor especifico; retorna string."""
        if isinstance(node, LiteralNode):
            return self._expr_literal(node)
        if isinstance(node, BinaryExprNode):
            return self._expr_binary(node)
        if isinstance(node, UnaryExprNode):
            return self._expr_unary(node)
        if isinstance(node, IndexExprNode):
            return self._expr_index(node)
        if isinstance(node, CallExprNode):
            return self._expr_call(node)
        if isinstance(node, MemberAccessNode):
            return self._expr_member_access(node)
        raise NotImplementedError(
            f"expressao nao suportada: {type(node).__name__}"
        )

    def _expr_literal(self, node):
        """Emite literal: int/real crus, cadeia re-quotada, logico True/False, ident."""
        kind = node.kind
        value = node.value
        if kind == "int":
            return str(value)
        if kind == "real":
            return str(value)
        if kind == "cadeia":
            return self._requotar_cadeia(value)
        if kind == "logico":
            if value == "verdadeiro":
                return "True"
            if value == "falso":
                return "False"
            return "True" if value else "False"
        if kind == "ident":
            if value in _BUILTINS_RUNTIME:
                self._runtime_usado.add(value)
            return str(value)
        return str(value)

    def _requotar_cadeia(self, valor):
        """Re-insere aspas em cadeia. Preserva sequências de escape como \\n."""
        # Convertemos quebras de linha reais em \\n para evitar SyntaxError no Python
        valor = valor.replace("\n", "\\n")
        return f"\"{valor}\""

    def _expr_binary(self, node):
        """Emite (left op right) com parentetizacao total."""
        left = self._expr(node.left)
        right = self._expr(node.right)
        op = _OPERADORES_BIN.get(node.op, node.op)
        return f"({left} {op} {right})"

    def _expr_unary(self, node):
        """Emite (op operand) com parentetizacao total."""
        operand = self._expr(node.operand)
        op = _OPERADORES_UN.get(node.op, node.op)
        return f"({op} {operand})"

    def _expr_index(self, node):
        """Emite base[i] ou base[i][j]."""
        base = self._expr(node.base)
        indices = "".join(f"[{self._expr(i)}]" for i in node.indices)
        return f"{base}{indices}"

    def _expr_member_access(self, node):
        base = self._expr(node.base)
        return f"{base}.{node.membro}"

    def _expr_call(self, node):
        """Despacha chamada por nome: builtins de E/S, math, nativo, runtime ou direta."""
        callee = node.callee
        if isinstance(callee, LiteralNode) and callee.kind == "ident":
            nome = callee.value
        else:
            nome = self._expr(callee)

        args = [self._expr(a) for a in node.args]

        if nome == "escreva":
            if not args:
                return "print(sep=\"\", end=\"\")"
            inner = ", ".join(args)
            return f"print({inner}, sep=\"\", end=\"\")"
        if nome == "escreval":
            if not args:
                return "print()"
            inner = ", ".join(args)
            return f"print({inner})"
        if nome == "leia":
            if not node.args:
                return "input()"
            return self._leia_linha(node.args[0])
        if nome in _BUILTINS_MATH:
            self._usou_math = True
            inner = ", ".join(args)
            return f"{_BUILTINS_MATH[nome]}({inner})"
        if nome in _BUILTINS_NATIVOS:
            inner = ", ".join(args)
            return f"{_BUILTINS_NATIVOS[nome]}({inner})"
        if nome == "aleatorio":
            self._usou_random = True
            return "random.random()"
        if nome in _BUILTINS_RUNTIME:
            self._runtime_usado.add(nome)
            inner = ", ".join(args)
            return f"{nome}({inner})"

        inner = ", ".join(args)
        return f"{nome}({inner})"

    def _tipo_do_alvo(self, arg):
        """Resolve o tipo declarado do alvo de leitura, ou None se desconhecido.

        Consulta a tabela de simbolos (se fornecida) e a inferencia local do
        emissor (`_locais`/`_globais_escalares`). Alvos indexados ou nao
        identificadores devolvem None (fallback float a cargo do chamador).
        """
        if not (isinstance(arg, LiteralNode) and arg.kind == "ident"):
            return None
        nome = arg.value
        if self._tabela_simbolos is not None:
            tipo = self._tabela_simbolos.tipo_de(nome, self._funcao_atual)
            if tipo:
                return tipo
        return self._locais.get(nome) or self._globais_escalares.get(nome)

    def _leia_linha(self, arg):
        """Monta a linha de leitura de um alvo: '<alvo> = <conversor>(input())'.

        `logico` gera leitura booleana case-insensitive; tipo desconhecido cai
        no fallback `float` (FR-018, FR-019).
        """
        alvo = self._expr(arg)
        tipo = self._tipo_do_alvo(arg)
        if tipo == "inteiro":
            return f"{alvo} = int(input())"
        if tipo == "cadeia":
            return f"{alvo} = input()"
        if tipo == "logico":
            return f'{alvo} = input().strip().lower() in ("verdadeiro", "true", "1")'
        return f"{alvo} = float(input())"


def emitir(programa, tabela_simbolos=None):
    """Atalho equivalente a Emissor().gerar(programa, tabela_simbolos)."""
    return Emissor().gerar(programa, tabela_simbolos)
