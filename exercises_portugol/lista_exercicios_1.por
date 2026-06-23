// LISTA DE EXERCÍCIOS 1
// Exercícios com ENQUANTO e PARA em Portugol

// ============================================================
// EXERCÍCIO 1 - Sistema de Caixa (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		real valor, total = 0.0

		escreva("=== EXERCÍCIO 1: Sistema de Caixa ===\n")
		escreva("Digite os valores das compras (0 para finalizar):\n")

		leia(valor)
		enquanto(valor != 0) {
			total = total + valor
			leia(valor)
		}

		escreva("Total da compra: R$ ", total, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 2 - Sistema de Senha (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		cadeia senha, senhaCorreta = "1234"

		escreva("=== EXERCÍCIO 2: Sistema de Senha ===\n")
		escreva("Digite a senha para acesso:\n")

		leia(senha)
		enquanto(senha != senhaCorreta) {
			escreva("Senha incorreta! Tente novamente:\n")
			leia(senha)
		}

		escreva("Acesso liberado!\n\n")
	}
}

// ============================================================
// EXERCÍCIO 3 - Registro de Notas (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		real nota, soma = 0.0
		inteiro quantidade = 0

		escreva("=== EXERCÍCIO 3: Registro de Notas ===\n")
		escreva("Digite as notas dos alunos (valor negativo para finalizar):\n")

		leia(nota)
		enquanto(nota >= 0) {
			soma = soma + nota
			quantidade = quantidade + 1
			leia(nota)
		}

		se(quantidade > 0) {
			escreva("Média das notas: ", soma / quantidade, "\n")
		} senao {
			escreva("Nenhuma nota foi informada.\n")
		}
		escreva("\n")
	}
}

// ============================================================
// EXERCÍCIO 4 - Análise de Idade (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		inteiro idade, maioresDeIdade = 0

		escreva("=== EXERCÍCIO 4: Análise de Idade ===\n")
		escreva("Digite as idades das pessoas (0 para finalizar):\n")

		leia(idade)
		enquanto(idade != 0) {
			se(idade >= 18) {
				maioresDeIdade = maioresDeIdade + 1
			}
			leia(idade)
		}

		escreva("Quantidade de maiores de idade: ", maioresDeIdade, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 5 - Registro de Gastos (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		real valor, totalGasto = 0.0

		escreva("=== EXERCÍCIO 5: Registro de Gastos ===\n")
		escreva("Digite os valores gastos (0 para finalizar):\n")

		leia(valor)
		enquanto(valor != 0) {
			totalGasto = totalGasto + valor
			leia(valor)
		}

		escreva("Total gasto: R$ ", totalGasto, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 6 - Média de 5 Alunos (PARA)
// ============================================================
programa {
	funcao inicio() {
		real nota, soma = 0.0
		inteiro i

		escreva("=== EXERCÍCIO 6: Média de 5 Alunos ===\n")

		para(i = 1; i <= 5; i++) {
			escreva("Digite a nota do aluno ", i, ": ")
			leia(nota)
			soma = soma + nota
		}

		escreva("Média das notas: ", soma / 5, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 7 - Repetições de Exercício (PARA)
// ============================================================
programa {
	funcao inicio() {
		inteiro i

		escreva("=== EXERCÍCIO 7: Repetições do Exercício ===\n")
		escreva("Repetições: ")

		para(i = 1; i <= 10; i++) {
			escreva(i, " ")
		}

		escreva("\n\n")
	}
}

// ============================================================
// EXERCÍCIO 8 - Total de Vendas em 7 Dias (PARA)
// ============================================================
programa {
	funcao inicio() {
		real venda, totalVendas = 0.0
		inteiro dia

		escreva("=== EXERCÍCIO 8: Total de Vendas em 7 Dias ===\n")

		para(dia = 1; dia <= 7; dia++) {
			escreva("Digite o valor das vendas do dia ", dia, ": ")
			leia(venda)
			totalVendas = totalVendas + venda
		}

		escreva("Total vendido: R$ ", totalVendas, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 9 - Alunos Aprovados (PARA)
// ============================================================
programa {
	funcao inicio() {
		real nota
		inteiro i, aprovados = 0

		escreva("=== EXERCÍCIO 9: Alunos Aprovados ===\n")

		para(i = 1; i <= 6; i++) {
			escreva("Digite a nota do aluno ", i, ": ")
			leia(nota)
			se(nota >= 6) {
				aprovados = aprovados + 1
			}
		}

		escreva("Quantidade de alunos aprovados: ", aprovados, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 10 - Salários Acima de R$ 2000 (PARA)
// ============================================================
programa {
	funcao inicio() {
		real salario
		inteiro i, acima = 0

		escreva("=== EXERCÍCIO 10: Salários Acima de R$ 2000 ===\n")

		para(i = 1; i <= 8; i++) {
			escreva("Digite o salário do funcionário ", i, ": ")
			leia(salario)
			se(salario > 2000) {
				acima = acima + 1
			}
		}

		escreva("Quantidade de salários acima de R$ 2000: ", acima, "\n\n")
	}
}
