#!/bin/bash

# Arquivos de dados
ARQ_DADOS_VENDAS="dados_vendas.txt"
ARQ_CAIXA="vendas_caixa.txt"

# Verifica se os arquivos existem
if [ ! -f "$ARQ_DADOS_VENDAS" ]; then
    echo "[ERRO] O arquivo $ARQ_DADOS_VENDAS não foi encontrado. Registre o fechamento do dia primeiro."
    exit 1
fi

# Função para desenhar barra de gráfico simples com limite de tamanho
desenhar_barra() {
    local valor=$1
    local barra=""
    local max_barras=40 # Limite máximo de blocos na tela para não quebrar o layout

    # Se o valor passar de 40, travamos em 40 na tela para manter a formatação bonita
    if [ "$valor" -gt "$max_barras" ]; then
        valor=$max_barras
        limite_excedido=true
    else
        limite_excedido=false
    fi

    for (( i=0; i<$valor; i++ )); do
        barra="${barra}█"
    done
    
    # Coloca um sinalzinho de mais (+) no fim da barra se ela for maior que a tela
    if [ "$limite_excedido" = true ]; then
        barra="${barra}+"
    fi

    echo "$barra"
}

# ========================================================================
# FUNÇÃO PRINCIPAL DO DASHBOARD
# ========================================================================
exibir_dashboard() {
    clear # Limpa a tela antes de desenhar os novos dados
    
    DATA_HOJE=$(date +"%d/%m/%Y")
    DIA_SEMANA_HOJE=$(date +"%A")

    echo "=========================================================="
    echo "         📊 PAINEL DE INTELIGÊNCIA DA CANTINA 📊          "
    echo "=========================================================="
    echo ""

    # 1. Gráfico Sazonal e Dia que vende mais
    echo "----------------------------------------------------------"
    echo "1. GRÁFICO SAZONAL: Vendas por Dia da Semana"
    # A correção chave aqui é usar IFS='|' no laço while
    awk -F';' '{vendas[$2]+=$5} END {for (dia in vendas) print vendas[dia]"|"dia}' "$ARQ_DADOS_VENDAS" | sort -nr | while IFS='|' read -r qtd dia; do
        printf "%-15s | %-4s | %s\n" "$dia" "$qtd" "$(desenhar_barra "$qtd")"
    done

    echo ""
    # 2. Alimento mais vendido
    echo "----------------------------------------------------------"
    echo "2. ALIMENTO MAIS VENDIDO (Histórico Geral)"
    awk -F';' '{vendas[$3]+=$5} END {for (prod in vendas) print vendas[prod]"|"prod}' "$ARQ_DADOS_VENDAS" | sort -nr | head -n 3 | while IFS='|' read -r qtd prod; do
        printf "%-22s | %-5s unidades vendidas\n" "$prod" "$qtd"
    done

    echo ""
    # 3. Alimento que mais estraga/sobra
    echo "----------------------------------------------------------"
    echo "3. ALIMENTO QUE MAIS ESTRAGA (Maiores Sobras)"
    awk -F';' '{sobras[$3]+=$7} END {for (prod in sobras) print sobras[prod]"|"prod}' "$ARQ_DADOS_VENDAS" | sort -nr | head -n 3 | while IFS='|' read -r qtd prod; do
        printf "%-22s | %-5s unidades perdidas\n" "$prod" "$qtd"
    done

    echo ""
    # 4. Alimentos que geram MAIS e MENOS lucro
    echo "----------------------------------------------------------"
    echo "4. RANKING DE LUCRO DOS ALIMENTOS (R$)"
    echo "-> MAIS Lucrativos:"
    awk -F';' '{lucro[$3]+=$6} END {for (prod in lucro) printf "%.2f|%s\n", lucro[prod], prod}' "$ARQ_DADOS_VENDAS" | sort -n -r | head -n 3 | while IFS='|' read -r valor prod; do
        printf "   %-19s | R$ %s\n" "$prod" "$valor"
    done
    echo "-> MENOS Lucrativos (ou maior prejuízo):"
    awk -F';' '{lucro[$3]+=$6} END {for (prod in lucro) printf "%.2f|%s\n", lucro[prod], prod}' "$ARQ_DADOS_VENDAS" | sort -n | head -n 3 | while IFS='|' read -r valor prod; do
        printf "   %-19s | R$ %s\n" "$prod" "$valor"
    done

    echo ""
    # 5. Vendas e Sobras do Dia Atual
    echo "----------------------------------------------------------"
    echo "5. RESUMO DO DIA DE HOJE ($DATA_HOJE)"
    echo "-> VENDAS DE HOJE:"
    VENDAS_HOJE=$(awk -F';' -v data="$DATA_HOJE" '$1 == data {vendas+=$5} END {print vendas+0}' "$ARQ_DADOS_VENDAS")
    echo "   Total de itens vendidos hoje: $VENDAS_HOJE"

    echo "-> SOBRAS DE HOJE:"
    SOBRAS_HOJE=$(awk -F';' -v data="$DATA_HOJE" '$1 == data {sobras+=$7} END {print sobras+0}' "$ARQ_DADOS_VENDAS")
    echo "   Total de itens que sobraram hoje: $SOBRAS_HOJE"

    echo ""
    # 6. Quantidade de itens para produzir no próximo dia útil
    echo "----------------------------------------------------------"
    echo "6. PREVISÃO DE PRODUÇÃO (Baseada em Média Histórica Diária)"
    awk -F';' '
    {
        vendas[$2";"$3]+=$5;
        dias[$2";"$3]++;
    } 
    END {
        for (chave in vendas) {
            split(chave, arr, ";");
            dia=arr[1];
            prod=arr[2];
            media=int(vendas[chave]/dias[chave] + 0.5);
            print dia"|"prod"|"media;
        }
    }' "$ARQ_DADOS_VENDAS" | sort | while IFS='|' read -r dia prod media; do
        printf "Para %-15s -> Produzir: %-4s | Produto: %s\n" "$dia" "$media" "$prod"
    done
    
    echo "=========================================================="
}

# ========================================================================
# SISTEMA DE MONITORAMENTO E ATUALIZAÇÃO (AUTO-REFRESH)
# ========================================================================

# Mostra o dashboard pela primeira vez
exibir_dashboard

# Pega o "carimbo de tempo" (timestamp) atual do arquivo
ULTIMA_MODIFICACAO=$(stat -c %Y "$ARQ_DADOS_VENDAS")

echo -e "\n[🟢] Modo de monitoramento ativado em tempo real."
echo "[!] O painel atualizará sozinho se houver novas vendas. Pressione Ctrl+C para sair."

# Loop infinito que verifica o arquivo a cada 2 segundos
while true; do
    MODIFICACAO_ATUAL=$(stat -c %Y "$ARQ_DADOS_VENDAS")
    
    # Se o carimbo de tempo mudar, significa que o arquivo foi alterado
    if [ "$MODIFICACAO_ATUAL" != "$ULTIMA_MODIFICACAO" ]; then
        exibir_dashboard
        ULTIMA_MODIFICACAO=$MODIFICACAO_ATUAL
        echo -e "\n[🔄] Atualizado automaticamente em: $(date +'%H:%M:%S')"
        echo "[🟢] Modo de monitoramento ativado em tempo real. Pressione Ctrl+C para sair."
    fi
    
    # Pausa de 2 segundos para não sobrecarregar o processador do computador
    sleep 2
done
