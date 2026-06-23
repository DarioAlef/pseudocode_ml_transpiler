programa {
  funcao inicio() {
    real valor_hora
    real horas_trabalhadas
    real salario

    escreva("Digite o valor da hora do trabalhador:")
    leia(valor_hora)
    escreva("Digite a quantidade de horas trabalhadas:")
    leia(horas_trabalhadas)

    salario = valor_hora * horas_trabalhadas

    escreva("O salário a ser recebido é: ", salario)
  }
}
