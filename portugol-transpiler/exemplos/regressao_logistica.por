programa {

  // ===== Configuração =====
  inteiro NUM_FEATURES = 4
  inteiro EPOCAS       = 2000
  real    TAXA         = 0.1

  // ===== Dados e modelo (globais) =====
  // O tamanho declarado é um hint de tipo; ler_csv substitui o conteúdo
  // pelas linhas reais do CSV (X e y crescem dinamicamente em Python).
  real X[5000][4]      // features (preenchido por ler_csv)
  real y[5000]         // rótulos 0/1
  real pesos[4]
  real intercepto = 0.0
  inteiro N = 0        // nº real de linhas lido do CSV

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

  // custo médio (log-loss) sobre o dataset
  funcao real custo() {
    real soma = 0.0
    para (inteiro i = 0; i < N; i++) {
      real p = prever(i)
      se (p < 0.0000000000001) { p = 0.0000000000001 }
      se (p > 0.9999999999999) { p = 0.9999999999999 }
      soma = soma - (y[i] * logaritmo(p) + (1.0 - y[i]) * logaritmo(1.0 - p))
    }
    retorne soma / N
  }

  // um passo de gradiente descendente sobre todo o dataset
  funcao treinar() {
    para (inteiro epoca = 0; epoca < EPOCAS; epoca++) {
      real grad_w[4]
      real grad_b = 0.0
      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        grad_w[j] = 0.0
      }

      para (inteiro i = 0; i < N; i++) {
        real erro = prever(i) - y[i]           // (ŷ - y)
        grad_b = grad_b + erro
        para (inteiro j = 0; j < NUM_FEATURES; j++) {
          grad_w[j] = grad_w[j] + erro * X[i][j]
        }
      }

      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        pesos[j] = pesos[j] - TAXA * (grad_w[j] / N)
      }
      intercepto = intercepto - TAXA * (grad_b / N)

      se (epoca % 200 == 0) {
        escreval("Epoca ", epoca, " | custo: ", custo())
      }
    }
  }

  // acurácia: fração de classes previstas corretamente
  funcao real acuracia() {
    inteiro acertos = 0
    para (inteiro i = 0; i < N; i++) {
      inteiro classe = 0
      se (prever(i) >= 0.5) { classe = 1 }
      se (classe == y[i]) { acertos = acertos + 1 }
    }
    retorne acertos / N
  }

  funcao inicio() {
    escreval("=== Regressao Logistica em Portugol ===")
    N = ler_csv("dados.csv", X, y)
    escreval("Linhas lidas: ", N)

    normalizar_zscore(X, N, NUM_FEATURES)   // padroniza as features (essencial!)

    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      pesos[j] = 0.0
    }
    intercepto = 0.0

    treinar()

    escreval("")
    escreval("Acuracia final: ", acuracia())
    escreval("Intercepto: ", intercepto)
    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      escreval("peso[", j, "] = ", pesos[j])
    }
    salvar_pesos("modelo.txt", pesos, intercepto)
  }
}
