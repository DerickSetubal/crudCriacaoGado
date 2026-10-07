from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import db, Lote, ManejoTrimestral, PastoCercado
from services.calc_service import calcular_ganho_manejo

bp_manejos = Blueprint('manejos', __name__, url_prefix='/manejos')

@bp_manejos.route('/')
def index():
    """Histórico consolidado de todos os ciclos de manejo trimestrais."""
    lote_id = request.args.get('lote_id', type=int)
    query = ManejoTrimestral.query
    
    if lote_id:
        query = query.filter_by(lote_id=lote_id)
        
    manejos = query.order_by(ManejoTrimestral.data_manejo.desc(), ManejoTrimestral.id.desc()).all()
    lotes = Lote.query.filter_by(status='Ativo').all()
    
    return render_template(
        'manejos/index.html',
        manejos=manejos,
        lotes=lotes,
        lote_id_selecionado=lote_id
    )


@bp_manejos.route('/novo', methods=['GET', 'POST'])
def novo():
    """
    Registro do Ciclo de Manejo Trimestral (a cada 3 meses):
    - Pesagem geral do lote
    - Vacinas aplicadas (Aftosa, Raiva, Clostridiose...)
    - Remédios aplicados (Vermífugos, Vitaminas, Inseticidas...)
    - Movimentação de pasto/cercado (se houver)
    - Cálculo automático de Ganho de Peso e GMD
    - Agendamento automático do próximo ciclo (+90 dias)
    """
    lote_id_pre = request.args.get('lote_id', type=int)
    lotes = Lote.query.filter_by(status='Ativo').all()
    pastos = PastoCercado.query.all()
    
    lote_selecionado = db.session.get(Lote, lote_id_pre) if lote_id_pre else (lotes[0] if lotes else None)
    
    if request.method == 'POST':
        try:
            lote_id = int(request.form.get('lote_id'))
            lote = db.get_or_404(Lote, lote_id)
            
            data_manejo_str = request.form.get('data_manejo', '').strip()
            data_manejo = (
                datetime.strptime(data_manejo_str, '%Y-%m-%d').date()
                if data_manejo_str else date.today()
            )
            
            peso_medio_kg = float(request.form.get('peso_medio_kg', 0.0))
            pasto_destino = request.form.get('pasto_destino', lote.pasto_atual).strip()
            
            vacinas_lista = request.form.getlist('vacinas_padrao')
            outras_vacinas = request.form.get('outras_vacinas', '').strip()
            if outras_vacinas:
                vacinas_lista.append(outras_vacinas)
            vacinas_str = ", ".join(vacinas_lista) if vacinas_lista else "Nenhuma"
            
            remedios_lista = request.form.getlist('remedios_padrao')
            outros_remedios = request.form.get('outros_remedios', '').strip()
            if outros_remedios:
                remedios_lista.append(outros_remedios)
            remedios_str = ", ".join(remedios_lista) if remedios_lista else "Nenhum"
            
            custo_insumos = float(request.form.get('custo_insumos', 0.0) or 0.0)
            observacoes = request.form.get('observacoes', '').strip()
            
            # Determinar ciclo número e data anterior
            total_anteriores = len(lote.manejos)
            ciclo_numero = total_anteriores + 1
            
            if total_anteriores > 0:
                ultimo_manejo = lote.manejos[-1]
                peso_anterior_kg = ultimo_manejo.peso_medio_kg
                data_anterior = ultimo_manejo.data_manejo
            else:
                peso_anterior_kg = lote.peso_chegada_medio
                data_anterior = lote.data_chegada
                
            # Calcular ganho zootécnico
            calc_ganho = calcular_ganho_manejo(
                peso_atual=peso_medio_kg,
                peso_anterior=peso_anterior_kg,
                data_atual=data_manejo,
                data_anterior=data_anterior
            )
            
            manejo = ManejoTrimestral(
                lote_id=lote.id,
                ciclo_numero=ciclo_numero,
                data_manejo=data_manejo,
                dias_desde_ultimo=calc_ganho['dias'],
                peso_medio_kg=peso_medio_kg,
                peso_anterior_kg=peso_anterior_kg,
                ganho_peso_kg=calc_ganho['ganho_peso'],
                gmd_kg=calc_ganho['gmd'],
                arrobas_atual=round(peso_medio_kg / 30.0, 2),
                vacinas=vacinas_str,
                remedios=remedios_str,
                pasto_destino=pasto_destino,
                custo_insumos=custo_insumos,
                observacoes=observacoes
            )
            
            db.session.add(manejo)
            
            # Atualizar localização do lote e data do próximo manejo trimestral (+90 dias)
            lote.pasto_atual = pasto_destino
            lote.data_proximo_manejo = data_manejo + timedelta(days=90)
            
            db.session.commit()
            
            flash(
                f'Ciclo de manejo #{ciclo_numero} do lote {lote.codigo} registrado com sucesso! '
                f'Ganho no período: {calc_ganho["ganho_peso"]:+.1f} kg (GMD: {calc_ganho["gmd"]:.3f} kg/dia). '
                f'Próximo ciclo previsto: {lote.data_proximo_manejo.strftime("%d/%m/%Y")}.',
                'success'
            )
            return redirect(url_for('lotes.detalhe', id=lote.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar ciclo de manejo: {str(e)}', 'danger')
            
    return render_template(
        'manejos/novo.html',
        lotes=lotes,
        pastos=pastos,
        lote_selecionado=lote_selecionado
    )


@bp_manejos.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    """Exclui um registro de manejo e recalcula o próximo agendamento."""
    manejo = db.get_or_404(ManejoTrimestral, id)
    lote = manejo.lote
    try:
        db.session.delete(manejo)
        db.session.commit()
        
        # Recalcular próximo manejo
        lote.recalcular_proximo_manejo()
        db.session.commit()
        
        flash('Registro de manejo excluído com sucesso.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir manejo: {str(e)}', 'danger')
        
    return redirect(url_for('lotes.detalhe', id=lote.id))
