from datetime import date
from flask import Blueprint, render_template, jsonify
from models import db, Lote, ManejoTrimestral, PastoCercado

bp_dashboard = Blueprint('dashboard', __name__)

@bp_dashboard.route('/')
def index():
    """Página principal da Dashboard Interativa."""
    lotes = Lote.query.filter_by(status='Ativo').all()
    pastos = PastoCercado.query.all()
    
    total_lotes = len(lotes)
    total_cabecas = sum(l.quantidade_cabecas for l in lotes)
    investimento_total = sum(l.valor_total_aquisicao for l in lotes)
    
    # Peso médio do rebanho
    pesos_atuais = [l.peso_atual_medio for l in lotes]
    peso_medio = (sum(pesos_atuais) / len(pesos_atuais)) if pesos_atuais else 0.0
    
    # Ganho médio acumulado
    ganhos = [l.ganho_peso_total_acumulado for l in lotes]
    ganho_medio = (sum(ganhos) / len(ganhos)) if ganhos else 0.0
    
    # Total de arrobas atuais
    total_arrobas = sum(l.arrobas_atuais_totais for l in lotes)
    
    # Lotes com alerta de manejo trimestral
    hoje = date.today()
    lotes_atencao = []
    for l in lotes:
        st = l.status_manejo
        if st['status'] in ('Atrasado', 'Próximo'):
            lotes_atencao.append({
                'lote': l,
                'status_info': st
            })
            
    # Ordenar por prioridade (atrasados primeiro, depois próximos)
    lotes_atencao.sort(key=lambda x: (0 if x['status_info']['status'] == 'Atrasado' else 1, x['status_info']['dias']))
    
    # Últimos manejos registrados
    ultimos_manejos = (
        ManejoTrimestral.query
        .order_by(ManejoTrimestral.data_manejo.desc(), ManejoTrimestral.id.desc())
        .limit(5)
        .all()
    )
    
    return render_template(
        'dashboard.html',
        total_lotes=total_lotes,
        total_cabecas=total_cabecas,
        investimento_total=investimento_total,
        peso_medio=peso_medio,
        ganho_medio=ganho_medio,
        total_arrobas=total_arrobas,
        lotes_atencao=lotes_atencao,
        ultimos_manejos=ultimos_manejos,
        lotes=lotes,
        pastos=pastos
    )


@bp_dashboard.route('/api/dados-graficos')
def api_dados_graficos():
    """Retorna dados estruturados em JSON para renderização dos gráficos interativos."""
    lotes = Lote.query.filter_by(status='Ativo').all()
    pastos = PastoCercado.query.all()
    
    # 1. Gráfico de Evolução de Peso por Lote (Entrada vs Ciclos de Manejo)
    labels_lotes = []
    pesos_entrada = []
    pesos_atuais = []
    ganhos_kg = []
    
    for l in lotes:
        labels_lotes.append(l.codigo)
        pesos_entrada.append(round(l.peso_chegada_medio, 1))
        pesos_atuais.append(round(l.peso_atual_medio, 1))
        ganhos_kg.append(round(l.ganho_peso_total_acumulado, 1))
        
    # 2. Gráfico de Distribuição por Pasto/Cercado
    pasto_counts = {}
    for l in lotes:
        nome_pasto = l.pasto_atual or 'Não Definido'
        pasto_counts[nome_pasto] = pasto_counts.get(nome_pasto, 0) + l.quantidade_cabecas
        
    pastos_labels = list(pasto_counts.keys())
    pastos_valores = list(pasto_counts.values())
    
    # 3. Gráfico de Investimento vs Arrobas Atuais
    investimentos = [round(l.valor_total_aquisicao, 2) for l in lotes]
    arrobas = [round(l.arrobas_atuais_totais, 1) for l in lotes]
    
    return jsonify({
        'evolucao_peso': {
            'labels': labels_lotes,
            'pesos_entrada': pesos_entrada,
            'pesos_atuais': pesos_atuais,
            'ganhos': ganhos_kg
        },
        'distribuicao_pastos': {
            'labels': pastos_labels,
            'valores': pastos_valores
        },
        'financeiro_arrobas': {
            'labels': labels_lotes,
            'investimentos': investimentos,
            'arrobas': arrobas
        }
    })

