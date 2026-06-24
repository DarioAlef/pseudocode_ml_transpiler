# portugol-transpiler

Transpilador Portugol -> Python. Projeto academico com pipeline modular
linear (lexer -> parser -> AST -> emissor) e runtime isolado de E/S e ML.

## Uso basico

```bash
python transpilador.py <arquivo.por>            # gera <arquivo>.py (futuro)
python transpilador.py <arquivo.por> --run      # gera e executa (futuro)
python transpilador.py <arquivo.por> --tokens   # debug: imprime tokens (futuro)
python transpilador.py <arquivo.por> --ast      # debug: imprime a AST (futuro)
python transpilador.py --help                   # exibe a ajuda
```

> Nesta fase de scaffold apenas `--help` responde; as demais acoes sao
> no-op reservadas para fases futuras.

## Dependencias

Apenas a biblioteca padrao do Python 3.x (por isso `requirements.txt` esta
vazio).
