programa {

  // ===== Configuração =====
  inteiro NUM_FEATURES = 4
  inteiro EPOCAS       = 2000
  real    TAXA         = 0.1
  real    FRAC_TESTE   = 0.2

  // ===== Dados e modelo (globais) =====
  // O tamanho declarado é um hint de tipo; ler_csv substitui o conteúdo
  // pelas linhas reais do CSV (X e y crescem dinamicamente em Python).
  // Após dividir_treino_teste, as primeiras N_TR linhas são treino e as
  // restantes (de N_TR até N) são teste.
  real X[5000][4]      // features (preenchido por ler_csv)
  real y[5000]         // rótulos 0/1
  real pesos[4]
  real intercepto = 0.0
  inteiro N = 0        // nº total de linhas lido do CSV
  inteiro N_TR = 0     // nº de linhas de treino

  // sigmoide(z) = 1 / (1 + e^-z)
  funcao real sigmoide(real z) {
    retorne 1.0 / (1.0 + exp(-z))
  }

  // probabilidade prevista para a amostra i (valor em (0,1), NÃO a classe)
  // A classe é decidida depois: classe = 1 se prever(i) >= 0.5, senao 0.
  funcao real prever(inteiro i) {
    real z = intercepto
    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      z = z + pesos[j] * X[i][j]
    }
    retorne sigmoide(z)
  }

  // custo médio (log-loss) sobre o conjunto de TREINO (linhas 0..N_TR)
  funcao real custo() {
    real soma = 0.0
    para (inteiro i = 0; i < N_TR; i++) {
      real p = prever(i)
      se (p < 0.0000000000001) { p = 0.0000000000001 }
      se (p > 0.9999999999999) { p = 0.9999999999999 }
      soma = soma - (y[i] * logaritmo(p) + (1.0 - y[i]) * logaritmo(1.0 - p))
    }
    retorne soma / N_TR
  }

  // um passo de gradiente descendente sobre o conjunto de TREINO
  funcao treinar() {
    para (inteiro epoca = 0; epoca < EPOCAS; epoca++) {
      real grad_w[4]
      real grad_b = 0.0
      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        grad_w[j] = 0.0
      }

      para (inteiro i = 0; i < N_TR; i++) {
        real erro = prever(i) - y[i]           // (ŷ - y)
        grad_b = grad_b + erro
        para (inteiro j = 0; j < NUM_FEATURES; j++) {
          grad_w[j] = grad_w[j] + erro * X[i][j]
        }
      }

      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        pesos[j] = pesos[j] - TAXA * (grad_w[j] / N_TR)
      }
      intercepto = intercepto - TAXA * (grad_b / N_TR)

      se (epoca % 200 == 0) {
        escreval("Epoca ", epoca, " | custo: ", custo())
      }
    }
  }

  // acurácia sobre o conjunto de TESTE (linhas N_TR..N), nunca visto no treino
  funcao real acuracia_teste() {
    inteiro acertos = 0
    para (inteiro i = N_TR; i < N; i++) {
      inteiro classe = 0
      se (prever(i) >= 0.5) { classe = 1 }
      se (classe == y[i]) { acertos = acertos + 1 }
    }
    retorne acertos / (N - N_TR)
  }

  funcao inicio() {
    escreval("=== Regressao Logistica em Portugol ===")
    N = ler_csv("../portugol-transpiler/exemplos/dados.csv", X, y)
    escreval("Linhas lidas: ", N)

    // embaralha e separa treino/teste in-place; N_TR = nº de linhas de treino
    N_TR = dividir_treino_teste(X, y, FRAC_TESTE)
    escreval("Treino: ", N_TR, " | Teste: ", N - N_TR)

    // padroniza usando estatísticas SÓ do treino, aplicadas a treino e teste
    normalizar_treino_teste(X, N_TR, N, NUM_FEATURES)

    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      pesos[j] = 0.0
    }
    intercepto = 0.0

    treinar()

    escreval("")
    escreval("Acuracia final: ", acuracia_teste())
    escreval("Intercepto: ", intercepto)
    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      escreval("peso[", j, "] = ", pesos[j])
    }
    salvar_pesos("modelo.txt", pesos, intercepto)
  }
}
