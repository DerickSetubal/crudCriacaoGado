from datetime import date
from flask import Blueprint, request, jsonify
from models import db, Lote, PastoCercado
from services.calc_service import calcular_dados_lote, calcular_ganho_manejo

bp_api = Blueprint('api', __name__, url_prefix='/api')

@bp_api.route('/calcular-entrada', methods=['POST'])
def api_calcular_entrada():
    """Calcula valores em tempo real enquanto o usuário preenche o formulário de entrada."""
    data = request.get_json() or {}
    peso_medio = float(data.get('peso_chegada_medio', 0) or 0)
    quantidade = int(data.get('quantidade_cabecas', 1) or 1)
    valor_arroba = float(data.get('valor_arroba_pago', 0) or 0)
    
    res = calcular_dados_lote(peso_medio, quantidade, valor_arroba)
    return jsonify(res)


@bp_api.route('/lote/<int:id>/dados-manejo')
def api_dados_manejo_lote(id):
    """
    Retorna dados pré-carregados do lote para o formulário de ciclo trimestral,
    eliminando qualquer necessidade do produtor redigitar dados passados.
    """
    lote = db.get_or_404(Lote, id)
    
    total_manejos = len(lote.manejos)
    proximo_ciclo = total_manejos + 1
    
    if total_manejos > 0:
        ultimo = lote.manejos[-1]
        peso_anterior = ultimo.peso_medio_kg
        data_anterior = ultimo.data_manejo.strftime('%Y-%m-%d')
        data_anterior_formatada = ultimo.data_manejo.strftime('%d/%m/%Y')
    else:
        peso_anterior = lote.peso_chegada_medio
        data_anterior = lote.data_chegada.strftime('%Y-%m-%d')
        data_anterior_formatada = lote.data_chegada.strftime('%d/%m/%Y')
        
    return jsonify({
        'id': lote.id,
        'codigo': lote.codigo,
        'lote_origem': lote.lote_origem,
        'quantidade_cabecas': lote.quantidade_cabecas,
        'pasto_atual': lote.pasto_atual,
        'raca': lote.raca,
        'proximo_ciclo': proximo_ciclo,
        'peso_anterior_kg': peso_anterior,
        'data_anterior': data_anterior,
        'data_anterior_formatada': data_anterior_formatada,
        'data_sugerida': date.today().strftime('%Y-%m-%d')
    })


@bp_api.route('/calcular-manejo', methods=['POST'])
def api_calcular_manejo():
    """Calcula ganho de peso, arrobas ganhas e GMD em tempo real."""
    data = request.get_json() or {}
    peso_atual = float(data.get('peso_atual', 0) or 0)
    peso_anterior = float(data.get('peso_anterior', 0) or 0)
    data_atual = data.get('data_atual')
    data_anterior = data.get('data_anterior')
    
    if not data_atual or not data_anterior:
        return jsonify({'erro': 'Datas inválidas'}), 400
        
    res = calcular_ganho_manejo(peso_atual, peso_anterior, data_atual, data_anterior)
    return jsonify(res)
