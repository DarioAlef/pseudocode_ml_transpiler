// ============================================================
// Lista de Exercícios 1 – Estruturas Sequenciais (Módulo 2)
// ============================================================

// ------------------------------------------------------------
// Exercício 1
// Uma plataforma de cursos online precisa de um sistema simples
// para calcular a média final de um aluno. O sistema deve receber
// duas notas de avaliação e apresentar a média aritmética.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real nota1, nota2, media

    escreva("=== Sistema de Média Final ===\n")
    escreva("Digite a primeira nota: ")
    leia(nota1)
    escreva("Digite a segunda nota: ")
    leia(nota2)

    media = (nota1 + nota2) / 2

    escreva("Média aritmética do aluno: ", media)
  }
}

// ------------------------------------------------------------
// Exercício 2
// Uma rede de supermercados deseja automatizar parte do caixa.
// O operador informa o preço de um produto e a quantidade
// comprada. O sistema calcula o valor total da compra.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real preco, total
    inteiro quantidade

    escreva("=== Caixa do Supermercado ===\n")
    escreva("Informe o preço do produto: R$ ")
    leia(preco)
    escreva("Informe a quantidade comprada: ")
    leia(quantidade)

    total = preco * quantidade

    escreva("Valor total da compra: R$ ", total)
  }
}

// ------------------------------------------------------------
// Exercício 3
// Uma empresa de transporte quer acompanhar o consumo médio de
// combustível. O sistema recebe a distância percorrida e a
// quantidade de combustível utilizada, calculando o consumo
// médio em km por litro.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real distancia, combustivel, consumoMedio

    escreva("=== Consumo Médio de Combustível ===\n")
    escreva("Informe a distância percorrida (km): ")
    leia(distancia)
    escreva("Informe a quantidade de combustível utilizada (litros): ")
    leia(combustivel)

    consumoMedio = distancia / combustivel

    escreva("Consumo médio do veículo: ", consumoMedio, " km/l")
  }
}

// ------------------------------------------------------------
// Exercício 4
// Um restaurante deseja implementar um sistema que sugira
// automaticamente a gorjeta ao cliente. O sistema recebe o
// valor da conta, calcula 10% de gorjeta e mostra o total.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real valorConta, gorjeta, totalPagar

    escreva("=== Sistema de Gorjeta ===\n")
    escreva("Informe o valor da conta: R$ ")
    leia(valorConta)

    gorjeta = valorConta * 0.10
    totalPagar = valorConta + gorjeta

    escreva("Gorjeta sugerida (10%): R$ ", gorjeta, "\n")
    escreva("Valor total a pagar: R$ ", totalPagar)
  }
}

// ------------------------------------------------------------
// Exercício 5
// Uma empresa de RH precisa calcular o novo salário após
// reajuste. O sistema recebe o salário atual e o percentual
// de aumento e mostra o novo salário.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real salarioAtual, percentual, novoSalario

    escreva("=== Cálculo de Reajuste Salarial ===\n")
    escreva("Informe o salário atual: R$ ")
    leia(salarioAtual)
    escreva("Informe o percentual de aumento (%): ")
    leia(percentual)

    novoSalario = salarioAtual + (salarioAtual * percentual / 100)

    escreva("Novo salário após reajuste: R$ ", novoSalario)
  }
}

// ------------------------------------------------------------
// Exercício 6
// Uma empresa de arquitetura precisa calcular a área de paredes
// que serão pintadas. O sistema recebe a largura e a altura da
// parede e calcula a área da superfície.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real largura, altura, area

    escreva("=== Cálculo de Área de Parede ===\n")
    escreva("Informe a largura da parede (m): ")
    leia(largura)
    escreva("Informe a altura da parede (m): ")
    leia(altura)

    area = largura * altura

    escreva("Área da superfície a ser pintada: ", area, " m²")
  }
}

// ------------------------------------------------------------
// Exercício 7
// Uma empresa de turismo quer oferecer estimativa de gasto com
// combustível. O sistema recebe a distância, o consumo médio
// do veículo e o preço do combustível, calculando o custo total.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real distancia, consumoMedio, precoCombustivel, custoTotal

    escreva("=== Estimativa de Custo de Viagem ===\n")
    escreva("Informe a distância da viagem (km): ")
    leia(distancia)
    escreva("Informe o consumo médio do veículo (km/l): ")
    leia(consumoMedio)
    escreva("Informe o preço do combustível (R$/l): R$ ")
    leia(precoCombustivel)

    custoTotal = (distancia / consumoMedio) * precoCombustivel

    escreva("Custo total estimado com combustível: R$ ", custoTotal)
  }
}

// ------------------------------------------------------------
// Exercício 8
// Uma operadora de telefonia deseja gerar um relatório simples
// de uso diário. O sistema recebe a duração de três ligações
// e calcula o tempo total gasto em chamadas.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro ligacao1, ligacao2, ligacao3, totalMinutos

    escreva("=== Relatório de Uso Diário ===\n")
    escreva("Informe a duração da 1ª ligação (minutos): ")
    leia(ligacao1)
    escreva("Informe a duração da 2ª ligação (minutos): ")
    leia(ligacao2)
    escreva("Informe a duração da 3ª ligação (minutos): ")
    leia(ligacao3)

    totalMinutos = ligacao1 + ligacao2 + ligacao3

    escreva("Tempo total gasto em chamadas: ", totalMinutos, " minutos")
  }
}

// ------------------------------------------------------------
// Exercício 9
// Uma loja virtual deseja mostrar o valor médio de três produtos
// selecionados pelo cliente para comparação.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real preco1, preco2, preco3, media

    escreva("=== Comparação de Produtos ===\n")
    escreva("Informe o preço do 1º produto: R$ ")
    leia(preco1)
    escreva("Informe o preço do 2º produto: R$ ")
    leia(preco2)
    escreva("Informe o preço do 3º produto: R$ ")
    leia(preco3)

    media = (preco1 + preco2 + preco3) / 3

    escreva("Valor médio dos três produtos: R$ ", media)
  }
}

// ------------------------------------------------------------
// Exercício 10
// Uma empresa de mobilidade urbana precisa calcular o valor
// estimado de uma corrida. A tarifa consiste em uma taxa fixa
// de R$5,00 mais R$2,00 por quilômetro percorrido.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real distancia, valorTotal
    real taxaFixa = 5.00
    real tarifaKm = 2.00

    escreva("=== Cálculo de Corrida ===\n")
    escreva("Informe a distância da corrida (km): ")
    leia(distancia)

    valorTotal = taxaFixa + (tarifaKm * distancia)

    escreva("Valor total da corrida: R$ ", valorTotal)
  }
}


// ============================================================
// Lista de Exercícios 1 – Estruturas Condicionais (Módulo 3)
// ============================================================

// ------------------------------------------------------------
// Exercício 11
// Uma loja verifica se um cliente tem direito a brinde.
// Se o valor total da compra for >= R$200,00, o cliente
// recebe o brinde. Caso contrário, não recebe.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real valorCompra

    escreva("=== Sistema de Brinde Promocional ===\n")
    escreva("Informe o valor total da compra: R$ ")
    leia(valorCompra)

    se (valorCompra >= 200.00) {
      escreva("Parabéns! Você tem direito ao brinde!")
    } senao {
      escreva("Você não tem direito ao brinde. Compras acima de R$200,00 ganham brinde.")
    }
  }
}

// ------------------------------------------------------------
// Exercício 12
// Em uma escola, o aluno é aprovado se sua nota final for >= 6,0.
// Caso contrário, é reprovado.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real notaFinal

    escreva("=== Sistema de Aprovação Escolar ===\n")
    escreva("Informe a nota final do aluno: ")
    leia(notaFinal)

    se (notaFinal >= 6.0) {
      escreva("Situação: Aprovado")
    } senao {
      escreva("Situação: Reprovado")
    }
  }
}

// ------------------------------------------------------------
// Exercício 13
// Uma empresa de transporte verifica se uma encomenda pode
// seguir para entrega comum. Se o peso for <= 30 kg, segue
// normalmente. Caso contrário, vai para transporte especial.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real pesoEncomenda

    escreva("=== Verificação de Encomenda ===\n")
    escreva("Informe o peso da encomenda (kg): ")
    leia(pesoEncomenda)

    se (pesoEncomenda <= 30.0) {
      escreva("Encomenda liberada para entrega comum.")
    } senao {
      escreva("Encomenda encaminhada para transporte especial.")
    }
  }
}

// ------------------------------------------------------------
// Exercício 14
// Em um evento, a entrada em uma atividade exclusiva é permitida
// apenas para pessoas com 18 anos ou mais. Caso contrário,
// a entrada não será autorizada.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro idade

    escreva("=== Controle de Acesso ao Evento ===\n")
    escreva("Informe sua idade: ")
    leia(idade)

    se (idade >= 18) {
      escreva("Acesso autorizado. Bem-vindo à atividade!")
    } senao {
      escreva("Acesso não autorizado. Você precisa ter 18 anos ou mais.")
    }
  }
}

// ------------------------------------------------------------
// Exercício 15
// Uma biblioteca verifica se um usuário pode pegar um livro
// emprestado. Se ele possui cadastro ativo (1 = sim, 0 = não),
// o empréstimo é permitido. Caso contrário, não é realizado.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro cadastroAtivo

    escreva("=== Sistema de Empréstimo de Livros ===\n")
    escreva("O usuário possui cadastro ativo? (1 = Sim / 0 = Não): ")
    leia(cadastroAtivo)

    se (cadastroAtivo == 1) {
      escreva("Empréstimo permitido. Boas leituras!")
    } senao {
      escreva("Empréstimo não autorizado. Regularize seu cadastro.")
    }
  }
}

// ------------------------------------------------------------
// Exercício 16
// Um sistema de estacionamento cobra tarifa diferenciada.
// Se o veículo for uma motocicleta (1 = moto, 2 = carro),
// exibe "Tarifa de motocicleta". Caso contrário, "Tarifa de automóvel".
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro tipoVeiculo

    escreva("=== Sistema de Estacionamento ===\n")
    escreva("Informe o tipo de veículo (1 = Motocicleta / 2 = Automóvel): ")
    leia(tipoVeiculo)

    se (tipoVeiculo == 1) {
      escreva("Tarifa de motocicleta")
    } senao {
      escreva("Tarifa de automóvel")
    }
  }
}

// ------------------------------------------------------------
// Exercício 17
// Uma empresa verifica se um funcionário pode acessar uma área
// restrita. Se o crachá estiver ativo (1 = ativo, 0 = inativo),
// o acesso é liberado. Caso contrário, é bloqueado.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro statusCracha

    escreva("=== Controle de Acesso à Área Restrita ===\n")
    escreva("Informe a situação do crachá (1 = Ativo / 0 = Inativo): ")
    leia(statusCracha)

    se (statusCracha == 1) {
      escreva("Acesso liberado.")
    } senao {
      escreva("Acesso bloqueado. Crachá inativo.")
    }
  }
}

// ------------------------------------------------------------
// Exercício 18
// Uma plataforma de ensino verifica se um estudante concluiu
// uma atividade obrigatória (1 = concluiu, 0 = não concluiu).
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro atividadeConcluida

    escreva("=== Verificação de Atividade Obrigatória ===\n")
    escreva("O estudante concluiu a atividade? (1 = Sim / 0 = Não): ")
    leia(atividadeConcluida)

    se (atividadeConcluida == 1) {
      escreva("Atividade concluída")
    } senao {
      escreva("Atividade pendente")
    }
  }
}

// ------------------------------------------------------------
// Exercício 19
// Uma clínica verifica se um paciente pode ser atendido no
// horário prioritário. Se a idade for >= 60 anos, atendimento
// prioritário. Caso contrário, atendimento comum.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro idade

    escreva("=== Sistema de Atendimento da Clínica ===\n")
    escreva("Informe a idade do paciente: ")
    leia(idade)

    se (idade >= 60) {
      escreva("Atendimento prioritário")
    } senao {
      escreva("Atendimento comum")
    }
  }
}

// ------------------------------------------------------------
// Exercício 20
// Uma locadora verifica se um cliente pode alugar um veículo.
// Se o cliente tiver 21 anos ou mais, a locação é permitida.
// Caso contrário, não é permitida.
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro idadeCliente

    escreva("=== Sistema de Locação de Veículos ===\n")
    escreva("Informe a idade do cliente: ")
    leia(idadeCliente)

    se (idadeCliente >= 21) {
      escreva("Locação permitida. Bom passeio!")
    } senao {
      escreva("Locação não permitida. É necessário ter 21 anos ou mais.")
    }
  }
}


// ============================================================
// Lista de Exercícios 2 – Estruturas Condicionais (Módulo 3)
// ============================================================

// ------------------------------------------------------------
// Exercício 21
// Uma escola classifica o desempenho do aluno:
// Nota >= 9: "Excelente" | Nota >= 6: "Aprovado" | Nota < 6: "Reprovado"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real nota

    escreva("=== Classificação de Desempenho Escolar ===\n")
    escreva("Informe a nota final do aluno: ")
    leia(nota)

    se (nota >= 9.0) {
      escreva("Situação: Excelente")
    } senao se (nota >= 6.0) {
      escreva("Situação: Aprovado")
    } senao {
      escreva("Situação: Reprovado")
    }
  }
}

// ------------------------------------------------------------
// Exercício 22
// Uma empresa concede bônus conforme avaliação de desempenho:
// Nota >= 8: "Bônus alto" | Nota >= 6: "Bônus médio" | Nota < 6: "Sem bônus"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real notaAvaliacao

    escreva("=== Sistema de Bônus por Desempenho ===\n")
    escreva("Informe a nota de avaliação do funcionário: ")
    leia(notaAvaliacao)

    se (notaAvaliacao >= 8.0) {
      escreva("Tipo de bônus: Bônus alto")
    } senao se (notaAvaliacao >= 6.0) {
      escreva("Tipo de bônus: Bônus médio")
    } senao {
      escreva("Tipo de bônus: Sem bônus")
    }
  }
}

// ------------------------------------------------------------
// Exercício 23
// Uma transportadora classifica o tipo de frete pelo peso:
// Peso <= 10 kg: "Leve" | Peso <= 50 kg: "Médio" | Peso > 50 kg: "Pesado"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real peso

    escreva("=== Classificação de Frete ===\n")
    escreva("Informe o peso do produto (kg): ")
    leia(peso)

    se (peso <= 10.0) {
      escreva("Categoria de frete: Leve")
    } senao se (peso <= 50.0) {
      escreva("Categoria de frete: Médio")
    } senao {
      escreva("Categoria de frete: Pesado")
    }
  }
}

// ------------------------------------------------------------
// Exercício 24
// Uma empresa classifica candidatos pela idade:
// Idade < 18: "Não permitida" | Idade < 65: "Elegível" | Idade >= 65: "Aposentada"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro idade

    escreva("=== Classificação de Candidatos por Idade ===\n")
    escreva("Informe a idade do candidato: ")
    leia(idade)

    se (idade < 18) {
      escreva("Situação: Não permitida")
    } senao se (idade < 65) {
      escreva("Situação: Elegível")
    } senao {
      escreva("Situação: Aposentada")
    }
  }
}

// ------------------------------------------------------------
// Exercício 25
// Uma plataforma digital classifica usuários por pontos:
// Pontos < 100: "Iniciante" | Pontos < 500: "Avançado" | Pontos >= 500: "VIP"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    inteiro pontos

    escreva("=== Classificação de Usuários por Pontos ===\n")
    escreva("Informe a quantidade de pontos do usuário: ")
    leia(pontos)

    se (pontos < 100) {
      escreva("Classificação: Iniciante")
    } senao se (pontos < 500) {
      escreva("Classificação: Avançado")
    } senao {
      escreva("Classificação: VIP")
    }
  }
}

// ------------------------------------------------------------
// Exercício 26
// Uma escola avalia a frequência dos alunos:
// Frequência >= 75%: "Regular" | Frequência >= 50%: "Baixa" | Frequência < 50%: "Muito baixa"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real frequencia

    escreva("=== Avaliação de Frequência Escolar ===\n")
    escreva("Informe a frequência do aluno (%): ")
    leia(frequencia)

    se (frequencia >= 75.0) {
      escreva("Nível de frequência: Regular")
    } senao se (frequencia >= 50.0) {
      escreva("Nível de frequência: Baixa")
    } senao {
      escreva("Nível de frequência: Muito baixa")
    }
  }
}

// ------------------------------------------------------------
// Exercício 27
// Um sistema meteorológico classifica a temperatura:
// Temperatura < 15°C: "Frio" | Temperatura <= 25°C: "Agradável" | Temperatura > 25°C: "Quente"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real temperatura

    escreva("=== Sistema de Classificação Climática ===\n")
    escreva("Informe a temperatura ambiente (°C): ")
    leia(temperatura)

    se (temperatura < 15.0) {
      escreva("Condição do clima: Frio")
    } senao se (temperatura <= 25.0) {
      escreva("Condição do clima: Agradável")
    } senao {
      escreva("Condição do clima: Quente")
    }
  }
}

// ------------------------------------------------------------
// Exercício 28
// Uma empresa classifica o nível de risco de investimento:
// Valor < 1000: "Baixo risco" | Valor <= 10000: "Médio risco" | Valor > 10000: "Alto risco"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real valorInvestimento

    escreva("=== Classificação de Risco de Investimento ===\n")
    escreva("Informe o valor do investimento: R$ ")
    leia(valorInvestimento)

    se (valorInvestimento < 1000.0) {
      escreva("Classificação: Baixo risco")
    } senao se (valorInvestimento <= 10000.0) {
      escreva("Classificação: Médio risco")
    } senao {
      escreva("Classificação: Alto risco")
    }
  }
}

// ------------------------------------------------------------
// Exercício 29
// Um sistema de avaliação classifica a qualidade de produtos:
// Nota < 4: "Ruim" | Nota < 6: "Regular" | Nota < 8: "Bom" | Nota >= 8: "Excelente"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real notaProduto

    escreva("=== Avaliação de Qualidade de Produto ===\n")
    escreva("Informe a nota do produto (0 a 10): ")
    leia(notaProduto)

    se (notaProduto < 4.0) {
      escreva("Classificação: Ruim")
    } senao se (notaProduto < 6.0) {
      escreva("Classificação: Regular")
    } senao se (notaProduto < 8.0) {
      escreva("Classificação: Bom")
    } senao {
      escreva("Classificação: Excelente")
    }
  }
}

// ------------------------------------------------------------
// Exercício 30
// Uma empresa classifica pedidos pelo valor total:
// Valor < 100: "Pequeno" | Valor <= 500: "Médio" | Valor > 500: "Grande"
// ------------------------------------------------------------
programa {
  funcao inicio() {
    real valorPedido

    escreva("=== Classificação de Pedidos ===\n")
    escreva("Informe o valor total do pedido: R$ ")
    leia(valorPedido)

    se (valorPedido < 100.0) {
      escreva("Categoria do pedido: Pequeno")
    } senao se (valorPedido <= 500.0) {
      escreva("Categoria do pedido: Médio")
    } senao {
      escreva("Categoria do pedido: Grande")
    }
  }
}
