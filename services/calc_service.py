from datetime import date, datetime

def calcular_dados_lote(peso_medio, quantidade_cabecas, valor_arroba):
    """
    Calcula valores zootécnicos e financeiros na entrada do lote.
    Base de cálculo: 1 arroba (@) = 30 kg vivo (50% rendimento de carcaça).
    """
    peso_medio = float(peso_medio or 0.0)
    quantidade_cabecas = int(quantidade_cabecas or 0)
    valor_arroba = float(valor_arroba or 0.0)
    
    peso_total = round(peso_medio * quantidade_cabecas, 2)
    arrobas_por_cabeca = round(peso_medio / 30.0, 2)
    total_arrobas = round(arrobas_por_cabeca * quantidade_cabecas, 2)
    
    # Custo por cabeça e custo total
    custo_por_cabeca = round(arrobas_por_cabeca * valor_arroba, 2)
    custo_total = round(total_arrobas * valor_arroba, 2)
    
    return {
        'peso_total': peso_total,
        'arrobas_por_cabeca': arrobas_por_cabeca,
        'total_arrobas': total_arrobas,
        'custo_por_cabeca': custo_por_cabeca,
        'custo_total': custo_total
    }


def calcular_ganho_manejo(peso_atual, peso_anterior, data_atual, data_anterior):
    """
    Calcula o ganho líquido de peso, ganho em arrobas e o GMD (Ganho Médio Diário).
    """
    peso_atual = float(peso_atual or 0.0)
    peso_anterior = float(peso_anterior or 0.0)
    
    ganho_peso = round(peso_atual - peso_anterior, 2)
    ganho_arrobas = round(ganho_peso / 30.0, 2)
    
    if isinstance(data_atual, str):
        data_atual = datetime.strptime(data_atual, '%Y-%m-%d').date()
    if isinstance(data_anterior, str):
        data_anterior = datetime.strptime(data_anterior, '%Y-%m-%d').date()
        
    dias = max((data_atual - data_anterior).days, 1)
    gmd = round(ganho_peso / dias, 3) if dias > 0 else 0.0
    
    return {
        'dias': dias,
        'ganho_peso': ganho_peso,
        'ganho_arrobas': ganho_arrobas,
        'gmd': gmd
    }

