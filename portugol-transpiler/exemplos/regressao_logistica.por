programa {
  // Exemplo-alvo de validacao do transpilador (SC-005).
  // Regressao logistica simplificada em Portugol: le CSV, normaliza,
  // divide treino/teste, treina por gradiente descendente e salva pesos.

  funcao inicio() {
    real X_treino
    real y_treino
    real X_teste
    real y_teste

    real pesos
    real bias
    real taxa
    real epocas
    real i
    real previsto
    real erro
    real grad_p
    real grad_b

    X_treino = ler_csv("dados.csv")
    X_treino = normalizar_zscore(X_treino)

    real conjunto
    conjunto = dividir_treino_teste(X_treino, 0.8)

    pesos = 0.0
    bias = 0.0
    taxa = 0.1
    epocas = 100

    para (i = 0; i < epocas; i++) {
      previsto = exp(0.0)
      erro = previsto - y_treino
      grad_p = erro * X_treino
      grad_b = erro
      pesos = pesos - taxa * grad_p
      bias = bias - taxa * grad_b
    }

    salvar_pesos(pesos, bias)
  }
}
