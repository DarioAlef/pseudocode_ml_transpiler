"""Runtime isolado de E/S e suporte a ML do transpilador Portugol -> Python.

Responsabilidade: oferecer as primitivas de entrada/saida (leitura de CSV,
escrita de resultados) e funcoes de apoio a aprendizado de maquina
(normalizacao, etc.) usadas pelos programas transpilados. Mantem-se isolado
do pipeline de transpilacao para nao poluir os modulos do compilador. A
implementacao efetiva sera entregue em fase futura; neste scaffold o modulo
existe para reservar seu lugar e ser importavel.
"""
