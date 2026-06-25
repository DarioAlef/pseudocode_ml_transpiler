# portugol-transpiler

Transpilador Portugol -> Python. Projeto academico com pipeline modular
linear (lexer -> parser -> AST -> emissor) e runtime isolado de E/S e ML.

## Uso basico

```bash
python transpilador.py <arquivo.por>            # gera <arquivo>.py (futuro)
python transpilador.py <arquivo.por> --run      # gera e executa (futuro)
python transpilador.py <arquivo.por> --tokens   # depuracao: imprime os tokens
python transpilador.py <arquivo.por> --ast      # debug: imprime a AST (futuro)
python transpilador.py --help                   # exibe a ajuda
```

> Nesta fase, `--tokens` imprime a lista de tokens do arquivo informado
> (tipo, valor, linha/coluna), terminando em `EOF`. As demais acoes de
> transpilacao (`--run`, `--ast`) permanecem reservadas para fases futuras.

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
