"""Integration test para builtins de runtime: transpilação + execução ponta-a-ponta.

Cria um CSV temporário, transpila um programa .por que usa ler_csv ->
normalizar_zscore -> salvar_pesos -> carregar_pesos, escreve o .py, copia
o runtime e executa, validando ausência de ImportError/NameError e criação
do arquivo de pesos.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from ast_nodes import (
    BlockNode,
    CallExprNode,
    FunctionNode,
    LiteralNode,
    ProgramNode,
    VarDeclNode,
    TypeNode,
)
from emissor import Emissor


class TestBuiltinsRuntimeExec(unittest.TestCase):
    """Testa execução ponta-a-ponta de builtins de runtime."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.emissor = Emissor()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _criar_csv_temporario(self, path, linhas):
        """Cria um CSV temporário com as linhas fornecidas."""
        with open(path, "w") as f:
            for linha in linhas:
                f.write(linha + "\n")

    def _copiar_runtime(self, dir_destino):
        """Copia o runtime_portugol.py para o diretório de destino."""
        projeto_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        runtime_src = os.path.join(projeto_dir, "runtime_portugol.py")
        runtime_dst = os.path.join(dir_destino, "runtime_portugol.py")
        if os.path.exists(runtime_src):
            shutil.copy(runtime_src, runtime_dst)
        return runtime_dst

    def _montar_programa(self):
        """Monta programa .por que transpila para usar ler_csv -> normalizar_zscore -> salvar_pesos -> carregar_pesos."""
        global_X = VarDeclNode(
            tipo=TypeNode(base="real", is_array=True, dims=[
                LiteralNode(kind="int", value="100"),
                LiteralNode(kind="int", value="2"),
            ]),
            nome="X",
        )
        global_y = VarDeclNode(
            tipo=TypeNode(base="real", is_array=True, dims=[
                LiteralNode(kind="int", value="100"),
            ]),
            nome="y",
        )
        global_pesos = VarDeclNode(
            tipo=TypeNode(base="real", is_array=True, dims=[
                LiteralNode(kind="int", value="5"),
            ]),
            nome="pesos",
        )
        global_N = VarDeclNode(
            tipo=TypeNode(base="inteiro", is_array=False),
            nome="N",
        )

        args_ler = [
            LiteralNode(kind="cadeia", value="dados.csv"),
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="y"),
        ]
        call_ler = CallExprNode(
            callee=LiteralNode(kind="ident", value="ler_csv"),
            args=args_ler,
        )

        args_norm = [
            LiteralNode(kind="ident", value="X"),
            LiteralNode(kind="ident", value="N"),
            LiteralNode(kind="int", value="2"),
        ]
        call_norm = CallExprNode(
            callee=LiteralNode(kind="ident", value="normalizar_zscore"),
            args=args_norm,
        )

        args_salvar = [
            LiteralNode(kind="cadeia", value="pesos.txt"),
            LiteralNode(kind="ident", value="pesos"),
            LiteralNode(kind="real", value="0.5"),
        ]
        call_salvar = CallExprNode(
            callee=LiteralNode(kind="ident", value="salvar_pesos"),
            args=args_salvar,
        )

        args_carregar = [
            LiteralNode(kind="cadeia", value="pesos.txt"),
        ]
        call_carregar = CallExprNode(
            callee=LiteralNode(kind="ident", value="carregar_pesos"),
            args=args_carregar,
        )

        inicio = FunctionNode(
            nome="inicio",
            tipo_retorno=None,
            params=[],
            body=BlockNode(stmts=[call_ler, call_norm, call_salvar, call_carregar]),
        )

        return ProgramNode(
            funcoes=[inicio],
            globais=[global_X, global_y, global_pesos, global_N],
            dialeto="portugol_studio",
        )

    def test_executa_ler_csv_normalizar_zscore_salvar_carregar_pesos(self):
        """Executa transpilação e execução: ler_csv -> normalizar_zscore -> salvar_pesos -> carregar_pesos."""
        csv_path = os.path.join(self.temp_dir, "dados.csv")
        py_path = os.path.join(self.temp_dir, "programa.py")
        pesos_path = os.path.join(self.temp_dir, "pesos.txt")

        linhas_csv = [
            "1.0,2.0",
            "2.0,3.0",
            "3.0,4.0",
        ]
        self._criar_csv_temporario(csv_path, linhas_csv)

        self._copiar_runtime(self.temp_dir)

        programa = self._montar_programa()
        codigo_py = self.emissor.gerar(programa)

        with open(py_path, "w") as f:
            f.write(codigo_py)

        try:
            resultado = subprocess.run(
                [sys.executable, py_path],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=5,
            )

            self.assertEqual(
                resultado.returncode,
                0,
                f"Execução falhou:\nstdout: {resultado.stdout}\nstderr: {resultado.stderr}",
            )

            self.assertNotIn(
                "ImportError",
                resultado.stderr,
                f"ImportError encontrado:\n{resultado.stderr}",
            )

            self.assertNotIn(
                "NameError",
                resultado.stderr,
                f"NameError encontrado:\n{resultado.stderr}",
            )

            self.assertTrue(
                os.path.exists(pesos_path),
                f"Arquivo de pesos não foi criado em {pesos_path}",
            )

            with open(pesos_path, "r") as f:
                conteudo = f.read()
                self.assertGreater(
                    len(conteudo),
                    0,
                    "Arquivo de pesos está vazio",
                )

        except subprocess.TimeoutExpired:
            self.fail("Execução do programa expirou (timeout)")
        except Exception as e:
            self.fail(f"Erro ao executar programa: {e}")


if __name__ == "__main__":
    unittest.main()
