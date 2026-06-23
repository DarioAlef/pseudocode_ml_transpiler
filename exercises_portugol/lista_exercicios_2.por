// LISTA DE EXERCÍCIOS 2
// Exercícios com ENQUANTO e PARA em Portugol

// ============================================================
// EXERCÍCIO 1 - Sistema de Estacionamento (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		real valor, totalArrecadado = 0.0

		escreva("=== EXERCÍCIO 1: Sistema de Estacionamento ===\n")
		escreva("Digite os valores dos veículos (0 para finalizar):\n")

		leia(valor)
		enquanto(valor != 0) {
			totalArrecadado = totalArrecadado + valor
			leia(valor)
		}

		escreva("Total arrecadado: R$ ", totalArrecadado, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 2 - Aplicativo de Leitura (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		inteiro paginas, totalPaginas = 0

		escreva("=== EXERCÍCIO 2: Aplicativo de Leitura ===\n")
		escreva("Digite a quantidade de páginas lidas (0 para finalizar):\n")

		leia(paginas)
		enquanto(paginas != 0) {
			totalPaginas = totalPaginas + paginas
			leia(paginas)
		}

		escreva("Total de páginas lidas: ", totalPaginas, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 3 - Clínica - Média de Idades (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		inteiro idade, soma = 0, quantidade = 0

		escreva("=== EXERCÍCIO 3: Clínica - Média de Idades ===\n")
		escreva("Digite as idades dos pacientes (0 para finalizar):\n")

		leia(idade)
		enquanto(idade != 0) {
			soma = soma + idade
			quantidade = quantidade + 1
			leia(idade)
		}

		se(quantidade > 0) {
			escreva("Média das idades: ", soma / quantidade, "\n")
		} senao {
			escreva("Nenhum paciente foi registrado.\n")
		}
		escreva("\n")
	}
}

// ============================================================
// EXERCÍCIO 4 - Código Secreto - Contagem de Tentativas (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		cadeia codigo, codigoCorreto = "9876"
		inteiro tentativas = 0

		escreva("=== EXERCÍCIO 4: Código Secreto ===\n")
		escreva("Digite o código secreto:\n")

		leia(codigo)
		tentativas = 1
		enquanto(codigo != codigoCorreto) {
			escreva("Código incorreto! Tente novamente:\n")
			leia(codigo)
			tentativas = tentativas + 1
		}

		escreva("Código correto! Quantidade de tentativas: ", tentativas, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 5 - Produtos com Valor Superior a R$ 50 (ENQUANTO)
// ============================================================
programa {
	funcao inicio() {
		real valor
		inteiro quantidade = 0

		escreva("=== EXERCÍCIO 5: Produtos Acima de R$ 50 ===\n")
		escreva("Digite os valores dos produtos (0 para finalizar):\n")

		leia(valor)
		enquanto(valor != 0) {
			se(valor > 50) {
				quantidade = quantidade + 1
			}
			leia(valor)
		}

		escreva("Quantidade de produtos com valor superior a R$ 50: ", quantidade, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 6 - Soma das Notas de 5 Alunos (PARA)
// ============================================================
programa {
	funcao inicio() {
		real nota, soma = 0.0
		inteiro i

		escreva("=== EXERCÍCIO 6: Soma das Notas de 5 Alunos ===\n")

		para(i = 1; i <= 5; i++) {
			escreva("Digite a nota do aluno ", i, ": ")
			leia(nota)
			soma = soma + nota
		}

		escreva("Soma total das notas: ", soma, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 7 - Produção Diária em 6 Dias (PARA)
// ============================================================
programa {
	funcao inicio() {
		real producao, produtTotal = 0.0
		inteiro dia

		escreva("=== EXERCÍCIO 7: Produção Diária em 6 Dias ===\n")

		para(dia = 1; dia <= 6; dia++) {
			escreva("Digite a produção do dia ", dia, ": ")
			leia(producao)
			produtTotal = produtTotal + producao
		}

		escreva("Produção total: ", produtTotal, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 8 - Números Pares de 1 até 20 (PARA)
// ============================================================
programa {
	funcao inicio() {
		inteiro i

		escreva("=== EXERCÍCIO 8: Números Pares de 1 até 20 ===\n")
		escreva("Números pares: ")

		para(i = 2; i <= 20; i = i + 2) {
			escreva(i, " ")
		}

		escreva("\n\n")
	}
}

// ============================================================
// EXERCÍCIO 9 - Maior Peso Levantado em 8 Tentativas (PARA)
// ============================================================
programa {
	funcao inicio() {
		real peso, maiorPeso = 0.0
		inteiro i

		escreva("=== EXERCÍCIO 9: Maior Peso Levantado ===\n")

		para(i = 1; i <= 8; i++) {
			escreva("Digite o peso da tentativa ", i, ": ")
			leia(peso)
			se(peso > maiorPeso) {
				maiorPeso = peso
			}
		}

		escreva("Maior peso levantado: ", maiorPeso, "\n\n")
	}
}

// ============================================================
// EXERCÍCIO 10 - Produtos com Valor Inferior a R$ 30 (PARA)
// ============================================================
programa {
	funcao inicio() {
		real valor
		inteiro i, quantidade = 0

		escreva("=== EXERCÍCIO 10: Produtos Abaixo de R$ 30 ===\n")

		para(i = 1; i <= 10; i++) {
			escreva("Digite o valor do produto ", i, ": ")
			leia(valor)
			se(valor < 30) {
				quantidade = quantidade + 1
			}
		}

		escreva("Quantidade de produtos com valor inferior a R$ 30: ", quantidade, "\n\n")
	}
}
