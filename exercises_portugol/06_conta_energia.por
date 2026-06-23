programa {
  funcao inicio() {
    inteiro qtd_energia
    inteiro conta
    inteiro imposto
    inteiro total

    escreva("Quantos kWh foram cosumidos nesse mês? ")
    leia(qtd_energia)

    conta = qtd_energia * 0.75
    
    escreva("\nValor da conta sem imposto: R$", conta,",00")

    imposto = conta * 0.1

    escreva("\nValor do imposto: R$", imposto,",00")

    total = conta + imposto

    escreva("\nO valor total a ser pago (com imposto) R$", total,",00\n")
  }
}
