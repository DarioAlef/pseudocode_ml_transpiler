programa
{
    inclua biblioteca Arquivos --> arq
    inclua biblioteca Texto --> tx
    inclua biblioteca Tipos --> ti

    funcao inteiro ler_inteiro()
    {
        cadeia entrada
        leia(entrada)

        se (entrada == "")
        {
            retorne -1
        }

        retorne ti.cadeia_para_inteiro(entrada, 10)
    }

    funcao real ler_real()
    {
        cadeia entrada
        leia(entrada)

        se (entrada == "")
        {
            retorne -1.0
        }

        retorne ti.cadeia_para_real(entrada)
    }

    funcao inicializar_cardapio()
    {
        inteiro arquivo

        se (nao arq.arquivo_existe("./produtos.txt"))
        {
            arquivo = arq.abrir_arquivo("./produtos.txt", arq.MODO_ESCRITA)
            arq.escrever_linha("1;SALGADO;COXINHA;5.0;10.0\n", arquivo)
            arq.escrever_linha("2;DOCE;BRIGADEIRO;3.0;7.0\n", arquivo)
            arq.escrever_linha("3;BEBIDA;COCA-COLA;3.0;7.0\n", arquivo)
            arq.escrever_linha("4;DOCE;PIRULITO;2.0;5.0\n", arquivo)
            arq.fechar_arquivo(arquivo)
        }
    }

    funcao cadastrar_produto()
    {
        inteiro arquivo
        inteiro id = 1
        inteiro maior_id = 0
        inteiro pos_separador
        inteiro id_atual
        inteiro opcao_categoria = 0

        cadeia categoria = "", nome, linha, id_str, pausa

        real custo, preco

        limpa()
        escreva("========================================\n")
        escreva("|               Recre.io               |\n")
        escreva("|         CADASTRO DE PRODUTO          |\n")
        escreva("========================================\n\n")

        // Auto-incremento do ID
        se (arq.arquivo_existe("./produtos.txt"))
        {
            arquivo = arq.abrir_arquivo("./produtos.txt", arq.MODO_LEITURA)

            enquanto (nao arq.fim_arquivo(arquivo))
            {
                linha = arq.ler_linha(arquivo)

                se (linha != "")
                {
                    pos_separador = tx.posicao_texto(";", linha, 0)

                    se (pos_separador > 0)
                    {
                        id_str = tx.extrair_subtexto(linha, 0, pos_separador)
                        id_atual = ti.cadeia_para_inteiro(id_str, 10)

                        se (id_atual > maior_id)
                        {
                            maior_id = id_atual
                        }
                    }
                }
            }

            arq.fechar_arquivo(arquivo)
            id = maior_id + 1
        }

        escreva("ID do produto: ", id, " (Gerado automaticamente)\n\n")

        // Menu de categorias
        enquanto (opcao_categoria < 1 ou opcao_categoria > 3)
        {
            escreva("Escolha a Categoria:\n")
            escreva("1 - SALGADO\n")
            escreva("2 - DOCE\n")
            escreva("3 - BEBIDA\n")
            escreva("Opção: ")
            opcao_categoria = ler_inteiro()

            escolha (opcao_categoria)
            {
                caso 1:
                    categoria = "SALGADO"
                    pare
                caso 2:
                    categoria = "DOCE"
                    pare
                caso 3:
                    categoria = "BEBIDA"
                    pare
                caso contrario:
                    escreva("\n[ERRO] Opção inválida! Tente novamente.\n\n")
            }
        }

        escreva("\nCategoria selecionada: ", categoria, "\n\n")

        escreva("Nome do produto: ")
        leia(nome)

        escreva("Custo de produção (R$): ")
        custo = ler_real()

        escreva("Preço de venda (R$): ")
        preco = ler_real()

        // Validação: preço deve ser maior que custo
        enquanto (preco <= custo)
        {
            escreva("\n[ERRO] O preço de venda não pode ser menor ou igual ao custo!\n")
            escreva("Por favor, digite um preço de venda válido (R$): ")
            preco = ler_real()
        }

        arquivo = arq.abrir_arquivo("./produtos.txt", arq.MODO_ACRESCENTAR)
        arq.escrever_linha(id + ";" + categoria + ";" + nome + ";" + custo + ";" + preco + "\n", arquivo)
        arq.fechar_arquivo(arquivo)

        escreva("\nProduto cadastrado com sucesso!\n\n")
        escreva("Pressione ENTER para voltar...")
        leia(pausa)
    }

    funcao listar_produtos()
    {
        inteiro arquivo
        inteiro pos1
        inteiro pos2
        inteiro pos3
        inteiro pos4

        cadeia linha, id, categoria, nome, custo, preco

        limpa()
        escreva("========================================\n")
        escreva("|               Recre.io               |\n")
        escreva("|         PRODUTOS CADASTRADOS         |\n")
        escreva("========================================\n\n")

        se (arq.arquivo_existe("./produtos.txt"))
        {
            arquivo = arq.abrir_arquivo("./produtos.txt", arq.MODO_LEITURA)

            enquanto (nao arq.fim_arquivo(arquivo))
            {
                linha = arq.ler_linha(arquivo)

                se (linha != "")
                {
                    // Estrutura: ID;CATEGORIA;NOME;CUSTO;PRECO
                    pos1 = tx.posicao_texto(";", linha, 0)
                    pos2 = tx.posicao_texto(";", linha, pos1 + 1)
                    pos3 = tx.posicao_texto(";", linha, pos2 + 1)
                    pos4 = tx.posicao_texto(";", linha, pos3 + 1)

                    id        = tx.extrair_subtexto(linha, 0, pos1)
                    categoria = tx.extrair_subtexto(linha, pos1 + 1, pos2)
                    nome      = tx.extrair_subtexto(linha, pos2 + 1, pos3)
                    custo     = tx.extrair_subtexto(linha, pos3 + 1, pos4)
                    preco     = tx.extrair_subtexto(linha, pos4 + 1, tx.numero_caracteres(linha))

                    escreva("[ ", id, " ] ", nome, "\n")
                    escreva("      Categoria : ", categoria, "\n")
                    escreva("      Custo     : R$ ", custo, "\n")
                    escreva("      Preco     : R$ ", preco, "\n\n")
                }
            }

            arq.fechar_arquivo(arquivo)
        }
        senao
        {
            escreva("Nenhum produto cadastrado ainda.\n")
        }

        escreva("Pressione ENTER para voltar...")
        leia(linha)
    }

    funcao cadeia buscar_linha_produto(inteiro id_busca)
    {
        inteiro arquivo
        inteiro pos_separador
        inteiro id_atual

        cadeia linha, id_str

        se (nao arq.arquivo_existe("./produtos.txt"))
        {
            retorne ""
        }

        arquivo = arq.abrir_arquivo("./produtos.txt", arq.MODO_LEITURA)

        enquanto (nao arq.fim_arquivo(arquivo))
        {
            linha = arq.ler_linha(arquivo)

            se (linha != "")
            {
                pos_separador = tx.posicao_texto(";", linha, 0)

                se (pos_separador > 0)
                {
                    id_str = tx.extrair_subtexto(linha, 0, pos_separador)
                    id_atual = ti.cadeia_para_inteiro(id_str, 10)

                    se (id_atual == id_busca)
                    {
                        arq.fechar_arquivo(arquivo)
                        retorne linha
                    }
                }
            }
        }

        arq.fechar_arquivo(arquivo)
        retorne ""
    }

    funcao exibir_produtos_paginado()
    {
        inteiro arquivo
        inteiro pos1
        inteiro pos2
        inteiro pos3
        inteiro pos4
        inteiro contador = 0

        cadeia linha, id, categoria, nome, custo, preco, navegacao

        se (nao arq.arquivo_existe("./produtos.txt"))
        {
            escreva("Nenhum produto cadastrado ainda.\n\n")
            retorne
        }

        arquivo = arq.abrir_arquivo("./produtos.txt", arq.MODO_LEITURA)

        enquanto (nao arq.fim_arquivo(arquivo))
        {
            linha = arq.ler_linha(arquivo)

            se (linha != "")
            {
                // Estrutura: ID;CATEGORIA;NOME;CUSTO;PRECO
                pos1 = tx.posicao_texto(";", linha, 0)
                pos2 = tx.posicao_texto(";", linha, pos1 + 1)
                pos3 = tx.posicao_texto(";", linha, pos2 + 1)
                pos4 = tx.posicao_texto(";", linha, pos3 + 1)

                id        = tx.extrair_subtexto(linha, 0, pos1)
                categoria = tx.extrair_subtexto(linha, pos1 + 1, pos2)
                nome      = tx.extrair_subtexto(linha, pos2 + 1, pos3)
                custo     = tx.extrair_subtexto(linha, pos3 + 1, pos4)
                preco     = tx.extrair_subtexto(linha, pos4 + 1, tx.numero_caracteres(linha))

                escreva("[ ", id, " ] ", nome, "\n")
                escreva("      Categoria : ", categoria, "\n")
                escreva("      Custo     : R$ ", custo, "\n")
                escreva("      Preco     : R$ ", preco, "\n\n")

                contador = contador + 1

                se (contador == 5 e nao arq.fim_arquivo(arquivo))
                {
                    escreva("------------------------------------------\n")
                    escreva("ENTER para ver mais | D para digitar o ID\n")
                    escreva("------------------------------------------\n")
                    leia(navegacao)

                    se (navegacao == "D" ou navegacao == "d")
                    {
                        arq.fechar_arquivo(arquivo)
                        retorne
                    }

                    limpa()
                    contador = 0
                }
            }
        }

        arq.fechar_arquivo(arquivo)
    }

    funcao lancar_sobra()
    {
        inteiro arquivo
        inteiro id_produto
        inteiro quantidade = 0
        inteiro pos1
        inteiro pos2
        inteiro pos3

        cadeia linha, nome, pausa, id_str

        limpa()
        escreva("========================================\n")
        escreva("|               Recre.io               |\n")
        escreva("|         LANCAMENTO DE SOBRAS         |\n")
        escreva("========================================\n\n")
        escreva("--- PRODUTOS DISPONÍVEIS ---\n\n")
        exibir_produtos_paginado()
        escreva("------------------------------------------\n\n")

        escreva("ID do produto: ")
        leia(id_str)

        se (id_str == "")
        {
            escreva("\n[ERRO] ID não pode ser vazio!\n\n")
            escreva("Pressione ENTER para voltar...")
            leia(pausa)
            retorne
        }

        id_produto = ti.cadeia_para_inteiro(id_str, 10)
        linha = buscar_linha_produto(id_produto)

        se (linha == "")
        {
            escreva("\n[ERRO] Produto não encontrado!\n\n")
            escreva("Pressione ENTER para voltar...")
            leia(pausa)
        }
        senao
        {
            // Estrutura: ID;CATEGORIA;NOME;CUSTO;PRECO
            pos1 = tx.posicao_texto(";", linha, 0)
            pos2 = tx.posicao_texto(";", linha, pos1 + 1)
            pos3 = tx.posicao_texto(";", linha, pos2 + 1)

            nome = tx.extrair_subtexto(linha, pos2 + 1, pos3)

            escreva("\nProduto: ", nome, "\n")

            escreva("Quantidade de sobra (unidades): ")
            quantidade = ler_inteiro()

            enquanto (quantidade <= 0)
            {
                escreva("\n[ERRO] A quantidade deve ser maior que zero!\n")
                escreva("Quantidade de sobra (unidades): ")
                quantidade = ler_inteiro()
            }

            arquivo = arq.abrir_arquivo("./sobras.txt", arq.MODO_ACRESCENTAR)
            arq.escrever_linha(id_produto + ";" + quantidade + "\n", arquivo)
            arq.fechar_arquivo(arquivo)

            escreva("\nSobra registrada com sucesso!\n\n")
            escreva("Pressione ENTER para voltar...")
            leia(pausa)
        }
    }

    funcao registrar_venda()
    {
        inteiro arquivo
        inteiro id_produto
        inteiro quantidade = 0
        inteiro pos1
        inteiro pos2
        inteiro pos3
        inteiro pos4

        real preco
        real valor_total

        cadeia linha, nome, pausa, id_str

        limpa()
        escreva("========================================\n")
        escreva("|               Recre.io               |\n")
        escreva("|          REGISTRO DE VENDA           |\n")
        escreva("========================================\n\n")
        escreva("--- PRODUTOS DISPONÍVEIS ---\n\n")
        exibir_produtos_paginado()
        escreva("------------------------------------------\n\n")

        escreva("ID do produto: ")
        leia(id_str)

        se (id_str == "")
        {
            escreva("\n[ERRO] ID não pode ser vazio!\n\n")
            escreva("Pressione ENTER para voltar...")
            leia(pausa)
            retorne
        }

        id_produto = ti.cadeia_para_inteiro(id_str, 10)
        linha = buscar_linha_produto(id_produto)

        se (linha == "")
        {
            escreva("\n[ERRO] Produto não encontrado!\n\n")
            escreva("Pressione ENTER para voltar...")
            leia(pausa)
        }
        senao
        {
            // Estrutura: ID;CATEGORIA;NOME;CUSTO;PRECO
            pos1 = tx.posicao_texto(";", linha, 0)
            pos2 = tx.posicao_texto(";", linha, pos1 + 1)
            pos3 = tx.posicao_texto(";", linha, pos2 + 1)
            pos4 = tx.posicao_texto(";", linha, pos3 + 1)

            nome = tx.extrair_subtexto(linha, pos2 + 1, pos3)
            preco = ti.cadeia_para_real(tx.extrair_subtexto(linha, pos4 + 1, tx.numero_caracteres(linha)))

            escreva("\nProduto: ", nome, "\n")
            escreva("Preço unitário: R$ ", preco, "\n\n")

            escreva("Quantidade vendida (unidades): ")
            quantidade = ler_inteiro()

            enquanto (quantidade <= 0)
            {
                escreva("\n[ERRO] A quantidade deve ser maior que zero!\n")
                escreva("Quantidade vendida (unidades): ")
                quantidade = ler_inteiro()
            }

            valor_total = quantidade * preco

            arquivo = arq.abrir_arquivo("./vendas.txt", arq.MODO_ACRESCENTAR)
            arq.escrever_linha(id_produto + ";" + quantidade + "\n", arquivo)
            arq.fechar_arquivo(arquivo)

            escreva("\nVenda registrada com sucesso!\n")
            escreva("Valor total da venda: R$ ", valor_total, "\n\n")
            escreva("Pressione ENTER para voltar...")
            leia(pausa)
        }
    }

    funcao relatorio_desperdicio()
    {
        inteiro arquivo
        inteiro id_produto
        inteiro quantidade
        inteiro pos_separador
        inteiro pos1
        inteiro pos2
        inteiro pos3
        inteiro pos4

        real custo
        real custo_sobra
        real total_desperdicio = 0.0

        cadeia linha, linha_produto, id_str, qtd_str, nome, pausa

        limpa()
        escreva("========================================\n")
        escreva("|               Recre.io               |\n")
        escreva("|       RELATORIO DE DESPERDICIO       |\n")
        escreva("========================================\n\n")

        se (arq.arquivo_existe("./sobras.txt"))
        {
            arquivo = arq.abrir_arquivo("./sobras.txt", arq.MODO_LEITURA)

            enquanto (nao arq.fim_arquivo(arquivo))
            {
                linha = arq.ler_linha(arquivo)

                se (linha != "")
                {
                    pos_separador = tx.posicao_texto(";", linha, 0)

                    se (pos_separador > 0)
                    {
                        id_str = tx.extrair_subtexto(linha, 0, pos_separador)
                        qtd_str = tx.extrair_subtexto(linha, pos_separador + 1, tx.numero_caracteres(linha))

                        id_produto = ti.cadeia_para_inteiro(id_str, 10)
                        quantidade = ti.cadeia_para_inteiro(qtd_str, 10)

                        linha_produto = buscar_linha_produto(id_produto)

                        se (linha_produto != "")
                        {
                            // Estrutura: ID;CATEGORIA;NOME;CUSTO;PRECO
                            pos1 = tx.posicao_texto(";", linha_produto, 0)
                            pos2 = tx.posicao_texto(";", linha_produto, pos1 + 1)
                            pos3 = tx.posicao_texto(";", linha_produto, pos2 + 1)
                            pos4 = tx.posicao_texto(";", linha_produto, pos3 + 1)

                            nome = tx.extrair_subtexto(linha_produto, pos2 + 1, pos3)
                            custo = ti.cadeia_para_real(tx.extrair_subtexto(linha_produto, pos3 + 1, pos4))
                            custo_sobra = quantidade * custo
                            total_desperdicio = total_desperdicio + custo_sobra

                            escreva("[ ", id_produto, " ] ", nome, "\n")
                            escreva("      Qtd Sobra   : ", quantidade, "\n")
                            escreva("      Custo Unit. : R$ ", custo, "\n")
                            escreva("      Custo Total : R$ ", custo_sobra, "\n\n")
                        }
                    }
                }
            }

            arq.fechar_arquivo(arquivo)

            escreva("----------------------------------------\n")
            escreva("CUSTO TOTAL DO DESPERDÍCIO: R$ ", total_desperdicio, "\n")
        }
        senao
        {
            escreva("Nenhuma sobra registrada ainda.\n")
        }

        escreva("\n\nPressione ENTER para voltar...")
        leia(pausa)
    }

    funcao relatorio_financeiro()
    {
        inteiro arquivo
        inteiro id_produto
        inteiro quantidade
        inteiro pos_separador
        inteiro pos1
        inteiro pos2
        inteiro pos3
        inteiro pos4

        real custo
        real preco
        real faturamento_bruto = 0.0
        real custo_vendido = 0.0
        real custo_desperdicio = 0.0
        real lucro_liquido = 0.0

        cadeia linha, linha_produto, id_str, qtd_str, pausa

        limpa()
        escreva("========================================\n")
        escreva("|               Recre.io               |\n")
        escreva("|         RELATORIO FINANCEIRO         |\n")
        escreva("========================================\n\n")

        se (arq.arquivo_existe("./vendas.txt"))
        {
            arquivo = arq.abrir_arquivo("./vendas.txt", arq.MODO_LEITURA)

            enquanto (nao arq.fim_arquivo(arquivo))
            {
                linha = arq.ler_linha(arquivo)

                se (linha != "")
                {
                    pos_separador = tx.posicao_texto(";", linha, 0)

                    se (pos_separador > 0)
                    {
                        id_str = tx.extrair_subtexto(linha, 0, pos_separador)
                        qtd_str = tx.extrair_subtexto(linha, pos_separador + 1, tx.numero_caracteres(linha))

                        id_produto = ti.cadeia_para_inteiro(id_str, 10)
                        quantidade = ti.cadeia_para_inteiro(qtd_str, 10)

                        linha_produto = buscar_linha_produto(id_produto)

                        se (linha_produto != "")
                        {
                            // Estrutura: ID;CATEGORIA;NOME;CUSTO;PRECO
                            pos1 = tx.posicao_texto(";", linha_produto, 0)
                            pos2 = tx.posicao_texto(";", linha_produto, pos1 + 1)
                            pos3 = tx.posicao_texto(";", linha_produto, pos2 + 1)
                            pos4 = tx.posicao_texto(";", linha_produto, pos3 + 1)

                            custo = ti.cadeia_para_real(tx.extrair_subtexto(linha_produto, pos3 + 1, pos4))
                            preco = ti.cadeia_para_real(tx.extrair_subtexto(linha_produto, pos4 + 1, tx.numero_caracteres(linha_produto)))

                            faturamento_bruto = faturamento_bruto + (quantidade * preco)
                            custo_vendido = custo_vendido + (quantidade * custo)
                        }
                    }
                }
            }

            arq.fechar_arquivo(arquivo)
        }

        se (arq.arquivo_existe("./sobras.txt"))
        {
            arquivo = arq.abrir_arquivo("./sobras.txt", arq.MODO_LEITURA)

            enquanto (nao arq.fim_arquivo(arquivo))
            {
                linha = arq.ler_linha(arquivo)

                se (linha != "")
                {
                    pos_separador = tx.posicao_texto(";", linha, 0)

                    se (pos_separador > 0)
                    {
                        id_str = tx.extrair_subtexto(linha, 0, pos_separador)
                        qtd_str = tx.extrair_subtexto(linha, pos_separador + 1, tx.numero_caracteres(linha))

                        id_produto = ti.cadeia_para_inteiro(id_str, 10)
                        quantidade = ti.cadeia_para_inteiro(qtd_str, 10)

                        linha_produto = buscar_linha_produto(id_produto)

                        se (linha_produto != "")
                        {
                            // Estrutura: ID;CATEGORIA;NOME;CUSTO;PRECO
                            pos1 = tx.posicao_texto(";", linha_produto, 0)
                            pos2 = tx.posicao_texto(";", linha_produto, pos1 + 1)
                            pos3 = tx.posicao_texto(";", linha_produto, pos2 + 1)
                            pos4 = tx.posicao_texto(";", linha_produto, pos3 + 1)

                            custo = ti.cadeia_para_real(tx.extrair_subtexto(linha_produto, pos3 + 1, pos4))
                            custo_desperdicio = custo_desperdicio + (quantidade * custo)
                        }
                    }
                }
            }

            arq.fechar_arquivo(arquivo)
        }

        lucro_liquido = faturamento_bruto - custo_vendido - custo_desperdicio

        escreva("Faturamento Bruto ..............: R$ ", faturamento_bruto, "\n")
        escreva("(-) Custo dos Produtos Vendidos : R$ ", custo_vendido, "\n")
        escreva("(-) Custo do Desperdício .......: R$ ", custo_desperdicio, "\n")
        escreva("----------------------------------------\n")
        escreva("Lucro Líquido ..................: R$ ", lucro_liquido, "\n")

        escreva("\n\nPressione ENTER para voltar...")
        leia(pausa)
    }

    funcao inicio()
    {
        inteiro opcao = -1

        inicializar_cardapio()

        enquanto (opcao != 0)
        {
            limpa()
            escreva("\n========================================\n")
            escreva("|               Recre.io               |\n")
            escreva("========================================\n\n")
            escreva("1 - Cadastrar produto\n")
            escreva("2 - Listar produtos\n")
            escreva("3 - Lançar sobra\n")
            escreva("4 - Registrar venda\n")
            escreva("5 - Relatório de desperdício\n")
            escreva("6 - Relatório financeiro\n")
            escreva("0 - Sair\n")
            escreva("\nEscolha: ")
            opcao = ler_inteiro()

            escolha (opcao)
            {
                caso 1:
                    cadastrar_produto()
                    pare
                caso 2:
                    listar_produtos()
                    pare
                caso 3:
                    lancar_sobra()
                    pare
                caso 4:
                    registrar_venda()
                    pare
                caso 5:
                    relatorio_desperdicio()
                    pare
                caso 6:
                    relatorio_financeiro()
                    pare
                caso 0:
                    escreva("\nEncerrando...\n")
                    pare
                caso contrario:
                    escreva("\n[ERRO] Opção inválida!\n")
            }
        }
    }
}