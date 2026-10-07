from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Lote, ManejoTrimestral, PastoCercado
from services.calc_service import calcular_dados_lote

bp_lotes = Blueprint('lotes', __name__, url_prefix='/lotes')

@bp_lotes.route('/')
def index():
    """Listagem de lotes com filtros dinâmicos."""
    busca = request.args.get('busca', '').strip()
    pasto_filtro = request.args.get('pasto', '').strip()
    status_filtro = request.args.get('status', '').strip()
    
    query = Lote.query
    
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            (Lote.codigo.ilike(termo)) | 
            (Lote.lote_origem.ilike(termo)) |
            (Lote.raca.ilike(termo))
        )
        
    if pasto_filtro:
        query = query.filter(Lote.pasto_atual == pasto_filtro)
        
    if status_filtro:
        query = query.filter(Lote.status == status_filtro)
        
    lotes = query.order_by(Lote.data_chegada.desc(), Lote.id.desc()).all()
    pastos = PastoCercado.query.all()
    
    return render_template(
        'lotes/index.html',
        lotes=lotes,
        pastos=pastos,
        busca=busca,
        pasto_filtro=pasto_filtro,
        status_filtro=status_filtro
    )


@bp_lotes.route('/novo', methods=['GET', 'POST'])
def novo():
    """Cadastro de entrada de um novo lote de gado na fazenda."""
    pastos = PastoCercado.query.filter_by(status='Ativo').all()
    
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo', '').strip()
            lote_origem = request.form.get('lote_origem', '').strip()
            data_chegada_str = request.form.get('data_chegada', '').strip()
            quantidade_cabecas = int(request.form.get('quantidade_cabecas', 1))
            peso_chegada_medio = float(request.form.get('peso_chegada_medio', 0.0))
            valor_arroba_pago = float(request.form.get('valor_arroba_pago', 0.0))
            pasto_atual = request.form.get('pasto_atual', '').strip()
            raca = request.form.get('raca', 'Nelore').strip()
            categoria = request.form.get('categoria', 'Boi Magro').strip()
            observacoes = request.form.get('observacoes', '').strip()
            
            # Validações essenciais
            if not codigo or not lote_origem or not pasto_atual:
                flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
                return render_template('lotes/form.html', pastos=pastos, form_data=request.form)
                
            if Lote.query.filter_by(codigo=codigo).first():
                flash(f'Já existe um lote cadastrado com o código "{codigo}".', 'warning')
                return render_template('lotes/form.html', pastos=pastos, form_data=request.form)
                
            data_chegada = (
                datetime.strptime(data_chegada_str, '%Y-%m-%d').date()
                if data_chegada_str else date.today()
            )
            
            # Cálculos automáticos de entrada
            calc = calcular_dados_lote(peso_chegada_medio, quantidade_cabecas, valor_arroba_pago)
            
            # Próximo manejo em 90 dias (trimestral)
            data_proximo_manejo = data_chegada + timedelta(days=90)
            
            novo_lote = Lote(
                codigo=codigo,
                lote_origem=lote_origem,
                data_chegada=data_chegada,
                quantidade_cabecas=quantidade_cabecas,
                peso_chegada_medio=peso_chegada_medio,
                peso_chegada_total=calc['peso_total'],
                valor_arroba_pago=valor_arroba_pago,
                valor_total_aquisicao=calc['custo_total'],
                pasto_atual=pasto_atual,
                raca=raca,
                categoria=categoria,
                status='Ativo',
                data_proximo_manejo=data_proximo_manejo,
                observacoes=observacoes
            )
            
            db.session.add(novo_lote)
            db.session.commit()
            
            flash(f'Lote "{codigo}" cadastrado com sucesso! Próximo manejo previsto para {data_proximo_manejo.strftime("%d/%m/%Y")}.', 'success')
            return redirect(url_for('lotes.detalhe', id=novo_lote.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar lote: {str(e)}', 'danger')
            return render_template('lotes/form.html', pastos=pastos, form_data=request.form)
            
    return render_template('lotes/form.html', pastos=pastos, form_data={})


@bp_lotes.route('/<int:id>')
def detalhe(id):
    """Ficha completa do lote com histórico de todos os manejos trimestrais."""
    lote = db.get_or_404(Lote, id)
    pastos = PastoCercado.query.all()
    
    # Histórico de pesagens para mini-gráfico
    historico_pesos = [{
        'data': lote.data_chegada.strftime('%d/%m/%Y'),
        'evento': 'Entrada',
        'peso': lote.peso_chegada_medio,
        'ganho': 0.0
    }]
    
    for m in lote.manejos:
        historico_pesos.append({
            'data': m.data_manejo.strftime('%d/%m/%Y'),
            'evento': f'{m.ciclo_numero}º Manejo (3m)',
            'peso': m.peso_medio_kg,
            'ganho': m.ganho_peso_kg
        })
        
    return render_template(
        'lotes/detalhe.html',
        lote=lote,
        pastos=pastos,
        historico_pesos=historico_pesos
    )


@bp_lotes.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    """Edição dos dados cadastrais do lote."""
    lote = db.get_or_404(Lote, id)
    pastos = PastoCercado.query.filter_by(status='Ativo').all()
    
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo', '').strip()
            lote_origem = request.form.get('lote_origem', '').strip()
            data_chegada_str = request.form.get('data_chegada', '').strip()
            quantidade_cabecas = int(request.form.get('quantidade_cabecas', 1))
            peso_chegada_medio = float(request.form.get('peso_chegada_medio', 0.0))
            valor_arroba_pago = float(request.form.get('valor_arroba_pago', 0.0))
            pasto_atual = request.form.get('pasto_atual', '').strip()
            raca = request.form.get('raca', 'Nelore').strip()
            categoria = request.form.get('categoria', 'Boi Magro').strip()
            status = request.form.get('status', 'Ativo').strip()
            observacoes = request.form.get('observacoes', '').strip()
            
            # Verificar código duplicado
            outro_lote = Lote.query.filter(Lote.codigo == codigo, Lote.id != lote.id).first()
            if outro_lote:
                flash(f'Já existe outro lote utilizando o código "{codigo}".', 'warning')
                return render_template('lotes/form.html', lote=lote, pastos=pastos)
                
            calc = calcular_dados_lote(peso_chegada_medio, quantidade_cabecas, valor_arroba_pago)
            
            lote.codigo = codigo
            lote.lote_origem = lote_origem
            if data_chegada_str:
                lote.data_chegada = datetime.strptime(data_chegada_str, '%Y-%m-%d').date()
            lote.quantidade_cabecas = quantidade_cabecas
            lote.peso_chegada_medio = peso_chegada_medio
            lote.peso_chegada_total = calc['peso_total']
            lote.valor_arroba_pago = valor_arroba_pago
            lote.valor_total_aquisicao = calc['custo_total']
            lote.pasto_atual = pasto_atual
            lote.raca = raca
            lote.categoria = categoria
            lote.status = status
            lote.observacoes = observacoes
            
            # Recalcular próximo manejo
            lote.recalcular_proximo_manejo()
            
            db.session.commit()
            flash(f'Lote "{codigo}" atualizado com sucesso!', 'success')
            return redirect(url_for('lotes.detalhe', id=lote.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar lote: {str(e)}', 'danger')
            
    return render_template('lotes/form.html', lote=lote, pastos=pastos)


@bp_lotes.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    """Exclusão de lote e seus ciclos vinculados."""
    lote = db.get_or_404(Lote, id)
    codigo = lote.codigo
    try:
        db.session.delete(lote)
        db.session.commit()
        flash(f'Lote "{codigo}" e todos os seus manejos foram excluídos com sucesso.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir lote: {str(e)}', 'danger')
        
    return redirect(url_for('lotes.index'))
