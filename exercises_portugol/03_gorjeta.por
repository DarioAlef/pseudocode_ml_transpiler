programa {
  funcao inicio() {
    real gorjeta
    real total_conta

    escreva("Digite o total da conta:")
    leia(total_conta)

    gorjeta = (total_conta * 0.1)

    escreva("O total da conta com gorjeta é: ", (total_conta + gorjeta))

  }
}
