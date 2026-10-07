import os
from datetime import datetime
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for, current_app
from models import db, Lote, ManejoTrimestral, PastoCercado, PlanilhaConsolidada
from services.excel_service import gerar_planilha_consolidada

bp_planilhas = Blueprint('planilhas', __name__, url_prefix='/planilhas')

@bp_planilhas.route('/')
def index():
    """Módulo de Histórico de Planilhas Consolidadas por Mês/Trimestre."""
    planilhas = PlanilhaConsolidada.query.order_by(PlanilhaConsolidada.data_geracao.desc()).all()
    
    # Métricas atuais para exibição do status antes de exportar
    lotes_ativos = Lote.query.filter_by(status='Ativo').all()
    total_cabecas = sum(l.quantidade_cabecas for l in lotes_ativos)
    investimento_total = sum(l.valor_total_aquisicao for l in lotes_ativos)
    
    pesos = [l.peso_atual_medio for l in lotes_ativos]
    peso_medio = (sum(pesos) / len(pesos)) if pesos else 0.0
    
    return render_template(
        'planilhas/index.html',
        planilhas=planilhas,
        lotes_count=len(lotes_ativos),
        total_cabecas=total_cabecas,
        peso_medio=peso_medio,
        investimento_total=investimento_total
    )


@bp_planilhas.route('/exportar-atual')
def exportar_atual():
    """Gera e faz o download imediato da planilha consolidada com os dados vivos do sistema."""
    lotes = Lote.query.order_by(Lote.data_chegada.desc()).all()
    pastos = PastoCercado.query.all()
    
    data_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    nome_arquivo = f"Relatorio_Pecuaria_Consolidado_{data_str}.xlsx"
    
    stream = gerar_planilha_consolidada(
        lotes=lotes,
        pastos=pastos,
        titulo_relatorio="Relatório Executivo da Pecuária (Dados Atuais)"
    )
    
    return send_file(
        stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=nome_arquivo
    )


@bp_planilhas.route('/consolidar', methods=['POST'])
def consolidar():
    """
    Cria e salva um snapshot/fechamento consolidado (Trimestral ou Mensal) no histórico.
    O arquivo físico é gerado e arquivado para consulta futura sem retrabalho.
    """
    try:
        titulo = request.form.get('titulo', '').strip()
        periodo_referencia = request.form.get('periodo_referencia', '').strip()
        tipo_periodo = request.form.get('tipo_periodo', 'Trimestral').strip()
        observacoes = request.form.get('observacoes', '').strip()
        
        if not periodo_referencia:
            flash('Informe o período de referência (ex: 2024-T1 ou Março/2024).', 'warning')
            return redirect(url_for('planilhas.index'))
            
        if not titulo:
            titulo = f"Consolidação {tipo_periodo} - {periodo_referencia}"
            
        lotes = Lote.query.all()
        pastos = PastoCercado.query.all()
        
        total_cabecas = sum(l.quantidade_cabecas for l in lotes)
        investimento_total = sum(l.valor_total_aquisicao for l in lotes)
        
        pesos = [l.peso_atual_medio for l in lotes]
        peso_medio = (sum(pesos) / len(pesos)) if pesos else 0.0
        
        ganhos = [l.ganho_peso_total_acumulado for l in lotes]
        ganho_medio = (sum(ganhos) / len(ganhos)) if ganhos else 0.0
        
        # Salvar arquivo físico na pasta exports
        exports_folder = current_app.config.get('EXPORTS_FOLDER')
        os.makedirs(exports_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_periodo = periodo_referencia.replace('/', '_').replace(' ', '_')
        nome_arquivo = f"Planilha_{tipo_periodo}_{safe_periodo}_{timestamp}.xlsx"
        caminho_arquivo = os.path.join(exports_folder, nome_arquivo)
        
        stream = gerar_planilha_consolidada(
            lotes=lotes,
            pastos=pastos,
            titulo_relatorio=f"Fechamento {tipo_periodo} - {periodo_referencia}"
        )
        
        with open(caminho_arquivo, 'wb') as f:
            f.write(stream.getvalue())
            
        # Registrar no banco
        registro = PlanilhaConsolidada(
            titulo=titulo,
            periodo_referencia=periodo_referencia,
            tipo_periodo=tipo_periodo,
            total_lotes=len(lotes),
            total_cabecas=total_cabecas,
            peso_medio_rebanho=round(peso_medio, 2),
            ganho_medio_kg=round(ganho_medio, 2),
            investimento_total_rebanho=round(investimento_total, 2),
            nome_arquivo=nome_arquivo,
            observacoes=observacoes
        )
        
        db.session.add(registro)
        db.session.commit()
        
        flash(f'Planilha consolidada "{titulo}" salva no histórico com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao consolidar planilha: {str(e)}', 'danger')
        
    return redirect(url_for('planilhas.index'))


@bp_planilhas.route('/<int:id>/download')
def download_historica(id):
    """Faz o download de uma planilha consolidada previamente salva no histórico."""
    planilha = db.get_or_404(PlanilhaConsolidada, id)
    exports_folder = current_app.config.get('EXPORTS_FOLDER')
    caminho = os.path.join(exports_folder, planilha.nome_arquivo) if planilha.nome_arquivo else None
    
    if caminho and os.path.exists(caminho):
        return send_file(
            caminho,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=planilha.nome_arquivo
        )
    else:
        # Se por algum motivo o arquivo físico não estiver no disco, gera dinamicamente
        lotes = Lote.query.all()
        pastos = PastoCercado.query.all()
        stream = gerar_planilha_consolidada(
            lotes=lotes,
            pastos=pastos,
            titulo_relatorio=f"Histórico: {planilha.titulo}"
        )
        nome_dl = planilha.nome_arquivo or f"Planilha_{planilha.periodo_referencia}.xlsx"
        return send_file(
            stream,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=nome_dl
        )


@bp_planilhas.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    """Exclui o registro histórico de planilha."""
    planilha = db.get_or_404(PlanilhaConsolidada, id)
    try:
        if planilha.nome_arquivo:
            exports_folder = current_app.config.get('EXPORTS_FOLDER')
            caminho = os.path.join(exports_folder, planilha.nome_arquivo)
            if os.path.exists(caminho):
                os.remove(caminho)
                
        db.session.delete(planilha)
        db.session.commit()
        flash('Registro de planilha consolidada removido com sucesso.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover registro: {str(e)}', 'danger')
        
    return redirect(url_for('planilhas.index'))
