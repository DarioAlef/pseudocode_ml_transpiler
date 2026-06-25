# portugol-transpiler

Transpilador Portugol -> Python. Projeto academico com pipeline modular
linear (lexer -> parser -> AST -> emissor) e runtime isolado de E/S e ML.

## Uso basico

```bash
python transpilador.py <arquivo.por>                       # gera portugol_out/<arquivo>.py
python transpilador.py <arquivo.por> --run                 # gera e executa o .py (cwd=portugol_out/)
python transpilador.py <arquivo.por> --tokens              # depuracao: imprime os tokens
python transpilador.py <arquivo.por> --ast                 # depuracao: imprime a AST
python transpilador.py <arquivo.por> --output-dir <DIR>    # define o diretorio de saida
python transpilador.py --help                              # exibe a ajuda
```

Por padrao, o `.py` gerado e o `runtime_portugol.py` sao escritos em
`./portugol_out/` (relativo ao diretorio de onde a CLI e invocada). Use
`--output-dir` para escolher outro destino; o diretorio e criado se ausente.
Os modos `--tokens` e `--ast` apenas imprimem diagnostico e nao gravam arquivo.

## Exemplo

```bash
python transpilador.py ../exercises_portugol/01_media_nota.por
# -> ./portugol_out/01_media_nota.py  e  ./portugol_out/runtime_portugol.py

python transpilador.py ../exercises_portugol/01_media_nota.por --run
# -> executa o .py gerado com CWD em ./portugol_out/
```

## Codigo de saida

- `0`: sucesso (ou `returncode` do programa filho com `--run`).
- `1`: arquivo inexistente ou erro lexico/sintatico (mensagem em `stderr`,
  sem traceback).

## Exemplo de regressao logistica (meta do projeto)

O exemplo `exemplos/regressao_logistica.por` treina uma regressao logistica
lendo `dados_sinteticos.csv`. Gere os dados sinteticos (reprodutiveis, semente
fixa) e rode o treino:

```bash
python exemplos/gerar_dados.py portugol_out/dados_sinteticos.csv
python transpilador.py exemplos/regressao_logistica.por --run
```

A saida mostra o custo diminuindo ao longo das epocas e a acuracia final
(>= 0.95). O gerador escreve um arquivo proprio; o `exemplos/dados.csv`
existente nao e modificado.

## Dependencias

Apenas a biblioteca padrao do Python 3.x (por isso `requirements.txt` esta
vazio).

## Testes

```bash
python -m pytest tests/contract tests/integration -q
ruff check .
```
