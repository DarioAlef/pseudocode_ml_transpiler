programa {

  // ===== Regressao Linear em Portugol (Recre.io) =====
  // Objetivo: prever a DEMANDA (quantidade vendida) de um item da cantina a
  // partir de features conhecidas ANTES de produzir. Assim a cantina decide
  // quanto produzir no dia seguinte e reduz desperdicio.
  //
  // Dataset: Recre.io/dados_treino.csv (gerado por aumentar_dados.py)
  //   features: produto_1..produto_7 (one-hot), dia_semana, preco_item  (9 col.)
  //   alvo:     qtd_vendida                            (ultima coluna, continuo)
  //
  // O produto (categorico) entra como 7 colunas one-hot, para o modelo aprender
  // um nivel de demanda por produto em vez de tratar o id como numero ordinal.
  // Se o numero de produtos mudar, ajuste NUM_FEATURES (produtos + 2) e os
  // tamanhos dos vetores abaixo -- o script imprime o valor correto.

  // ===== Configuracao =====
  inteiro NUM_FEATURES = 9
  inteiro EPOCAS       = 3000
  real    TAXA         = 0.1
  real    FRAC_TESTE   = 0.2
  inteiro DIA_ALVO     = 5   // dia a recomendar (1=Seg..7=Dom); 5 = Sexta ("amanha")

  // ===== Dados e modelo (globais) =====
  // O tamanho declarado e um hint de tipo; ler_csv substitui o conteudo pelas
  // linhas reais do CSV. Apos dividir_treino_teste, as primeiras N_TR linhas
  // sao treino e as restantes (N_TR..N) sao teste.
  real X[5000][9]      // features (preenchido por ler_csv)
  real y[5000]         // alvo continuo: quantidade vendida
  real previsoes[5000] // previsao do modelo por amostra (para o grafico)
  real pesos[9]
  real intercepto = 0.0
  inteiro N = 0        // nº total de linhas lido do CSV
  inteiro N_TR = 0     // nº de linhas de treino

  // predicao linear para a amostra i: y_hat = intercepto + soma(pesos[j] * X[i][j])
  funcao real prever(inteiro i) {
    real z = intercepto
    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      z = z + pesos[j] * X[i][j]
    }
    retorne z
  }

  // custo: erro quadratico medio (MSE) sobre o conjunto de TREINO (0..N_TR)
  funcao real custo() {
    real soma = 0.0
    para (inteiro i = 0; i < N_TR; i++) {
      real erro = prever(i) - y[i]
      soma = soma + erro * erro
    }
    retorne soma / N_TR
  }

  // um treinamento por gradiente descendente minimizando o MSE no TREINO
  funcao treinar() {
    para (inteiro epoca = 0; epoca < EPOCAS; epoca++) {
      real grad_w[9]
      real grad_b = 0.0
      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        grad_w[j] = 0.0
      }

      para (inteiro i = 0; i < N_TR; i++) {
        real erro = prever(i) - y[i]           // (y_hat - y)
        grad_b = grad_b + erro
        para (inteiro j = 0; j < NUM_FEATURES; j++) {
          grad_w[j] = grad_w[j] + erro * X[i][j]
        }
      }

      para (inteiro j = 0; j < NUM_FEATURES; j++) {
        pesos[j] = pesos[j] - TAXA * (grad_w[j] / N_TR)
      }
      intercepto = intercepto - TAXA * (grad_b / N_TR)

      se (epoca % 300 == 0) {
        escreval("Epoca ", epoca, " | MSE: ", custo())
      }
    }
  }

  // media do alvo no conjunto de TESTE (linhas N_TR..N)
  funcao real media_y_teste() {
    real soma = 0.0
    para (inteiro i = N_TR; i < N; i++) {
      soma = soma + y[i]
    }
    retorne soma / (N - N_TR)
  }

  // RMSE sobre o TESTE (nunca visto no treino): erro tipico em unidades vendidas
  funcao real rmse_teste() {
    real soma = 0.0
    para (inteiro i = N_TR; i < N; i++) {
      real erro = prever(i) - y[i]
      soma = soma + erro * erro
    }
    retorne raiz(soma / (N - N_TR))
  }

  // R2 (coeficiente de determinacao) sobre o TESTE: fracao da variancia explicada
  funcao real r2_teste() {
    real media = media_y_teste()
    real ss_res = 0.0
    real ss_tot = 0.0
    para (inteiro i = N_TR; i < N; i++) {
      real erro = prever(i) - y[i]
      ss_res = ss_res + erro * erro
      real desvio = y[i] - media
      ss_tot = ss_tot + desvio * desvio
    }
    retorne 1.0 - (ss_res / ss_tot)
  }

  funcao inicio() {
    escreval("=== Regressao Linear em Portugol (Recre.io) ===")
    N = ler_csv("../Recre.io/dados_treino.csv", X, y)
    escreval("Linhas lidas: ", N)

    // embaralha e separa treino/teste in-place; N_TR = nº de linhas de treino
    N_TR = dividir_treino_teste(X, y, FRAC_TESTE, 7)
    escreval("Treino: ", N_TR, " | Teste: ", N - N_TR)

    // padroniza as features usando estatisticas SO do treino (evita vazamento)
    normalizar_treino_teste(X, N_TR, N, NUM_FEATURES)

    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      pesos[j] = 0.0
    }
    intercepto = 0.0

    treinar()

    real RMSE = rmse_teste()
    real R2 = r2_teste()

    escreval("")
    escreval("RMSE teste (erro medio em unidades): ", RMSE)
    escreval("R2 teste (variancia explicada): ", R2)
    escreval("Intercepto: ", intercepto)
    para (inteiro j = 0; j < NUM_FEATURES; j++) {
      escreval("peso[", j, "] = ", pesos[j])
    }
    salvar_pesos("modelo.txt", pesos, intercepto)

    // registra as previsoes do conjunto de teste e gera os graficos SVG
    para (inteiro i = N_TR; i < N; i++) {
      previsoes[i] = prever(i)
    }
    // 1) real vs previsto por amostra   2) dispersao previsto x real (ajuste)
    plotar_previsoes("previsoes.svg", y, previsoes, N_TR, N, R2, RMSE)
    plotar_dispersao("dispersao.svg", y, previsoes, N_TR, N, R2, RMSE)
    // 3) recomendacao: quanto produzir de cada produto no dia alvo (usa o modelo)
    recomendar_producao("../Recre.io/dados_treino.csv", "recomendacao.svg",
                        pesos, intercepto, DIA_ALVO,
                        "../Recre.io/produtos_legenda.csv")

    escreval("")
    escreval("Graficos salvos (abra no navegador):")
    escreval("  previsoes.svg    - real vs previsto por amostra")
    escreval("  dispersao.svg    - previsto x real (qualidade do ajuste)")
    escreval("  recomendacao.svg - quanto produzir por produto no dia alvo")
  }
}
