import os
from datetime import date, timedelta
from app import create_app
from models import db, Lote, ManejoTrimestral, PastoCercado, PlanilhaConsolidada
from services.excel_service import gerar_planilha_consolidada

def popular_banco():
    app = create_app()
    with app.app_context():
        # Limpar dados antigos
        ManejoTrimestral.query.delete()
        PlanilhaConsolidada.query.delete()
        Lote.query.delete()
        PastoCercado.query.delete()
        db.session.commit()

        print("Populando pastos e cercados...")
        pastos = [
            PastoCercado(nome="Pasto 1 - Braquiária Sul", capacidade_cabecas=80, area_hectares=18.5, tipo_pasto="Brachiaria brizantha"),
            PastoCercado(nome="Pasto 2 - Piquete Mombaça", capacidade_cabecas=60, area_hectares=12.0, tipo_pasto="Panicum maximum Mombaça"),
            PastoCercado(nome="Pasto 3 - Cercado da Represa", capacidade_cabecas=100, area_hectares=22.0, tipo_pasto="Brachiaria decumbens"),
            PastoCercado(nome="Pasto 4 - Confinamento / Curral", capacidade_cabecas=120, area_hectares=5.0, tipo_pasto="Curral Coberto e Cocho"),
            PastoCercado(nome="Pasto 5 - Piquete Maternidade/Recria", capacidade_cabecas=50, area_hectares=10.0, tipo_pasto="Brachiaria humidicola"),
        ]
        db.session.add_all(pastos)
        db.session.commit()

        hoje = date.today()

        print("Populando lotes e ciclos de manejo trimestrais...")
        # Lote 1: Nelore Chegada há 190 dias (já passou por 2 manejos trimestrais: 3 meses e 6 meses)
        dt_chegada_1 = hoje - timedelta(days=190)
        dt_manejo_1a = dt_chegada_1 + timedelta(days=92)
        dt_manejo_1b = dt_manejo_1a + timedelta(days=90)
        
        lote1 = Lote(
            codigo="LOTE-2024-NELORE-A",
            lote_origem="Fazenda Santa Bárbara / MS",
            data_chegada=dt_chegada_1,
            quantidade_cabecas=45,
            peso_chegada_medio=330.0,
            peso_chegada_total=330.0 * 45,
            valor_arroba_pago=235.0,
            valor_total_aquisicao=round((330.0 / 30.0) * 45 * 235.0, 2),
            pasto_atual="Pasto 1 - Braquiária Sul",
            raca="Nelore PO / Comercial",
            categoria="Boi Magro",
            status="Ativo",
            data_proximo_manejo=dt_manejo_1b + timedelta(days=90),
            observacoes="Lote padronizado, excelente resposta à suplementação mineral no cocho."
        )
        db.session.add(lote1)
        db.session.flush()

        m1_1 = ManejoTrimestral(
            lote_id=lote1.id,
            ciclo_numero=1,
            data_manejo=dt_manejo_1a,
            dias_desde_ultimo=92,
            peso_anterior_kg=330.0,
            peso_medio_kg=395.0,
            ganho_peso_kg=65.0,
            gmd_kg=round(65.0 / 92, 3),
            arrobas_atual=round(395.0 / 30.0, 2),
            vacinas="Febre Aftosa, Clostridiose (Poli-Star)",
            remedios="Ivermectina 3.5%, Suplemento ADE Injetável",
            pasto_destino="Pasto 1 - Braquiária Sul",
            custo_insumos=1850.0,
            observacoes="Adaptação bem sucedida ao pasto. Nenhum animal refugo."
        )
        db.session.add(m1_1)

        m1_2 = ManejoTrimestral(
            lote_id=lote1.id,
            ciclo_numero=2,
            data_manejo=dt_manejo_1b,
            dias_desde_ultimo=90,
            peso_anterior_kg=395.0,
            peso_medio_kg=468.0,
            ganho_peso_kg=73.0,
            gmd_kg=round(73.0 / 90, 3),
            arrobas_atual=round(468.0 / 30.0, 2),
            vacinas="Raiva dos Herbívoros",
            remedios="Vermífugo Albendazol, Carrapaticida Pour-on",
            pasto_destino="Pasto 1 - Braquiária Sul",
            custo_insumos=1420.0,
            observacoes="Ótimo ganho de carcaça. Lote caminhando para fase de terminação."
        )
        db.session.add(m1_2)

        # Lote 2: Cruzamento Angus Chegada há 95 dias (Manejo trimestral atrasado há 5 dias - para testar alertas da UI)
        dt_chegada_2 = hoje - timedelta(days=95)
        lote2 = Lote(
            codigo="LOTE-2024-ANGUS-B",
            lote_origem="Leilão Genética do Sul / PR",
            data_chegada=dt_chegada_2,
            quantidade_cabecas=38,
            peso_chegada_medio=310.0,
            peso_chegada_total=310.0 * 38,
            valor_arroba_pago=245.0,
            valor_total_aquisicao=round((310.0 / 30.0) * 38 * 245.0, 2),
            pasto_atual="Pasto 2 - Piquete Mombaça",
            raca="Cruzamento Angus x Nelore",
            categoria="Garrote",
            status="Ativo",
            data_proximo_manejo=dt_chegada_2 + timedelta(days=90), # Ficou 5 dias no passado!
            observacoes="Animais de alta conversão alimentar. Aguardando fechamento trimestral no curral."
        )
        db.session.add(lote2)

        # Lote 3: Novilhos Senepol Chegada há 80 dias (Manejo próximo nos próximos 10 dias)
        dt_chegada_3 = hoje - timedelta(days=80)
        lote3 = Lote(
            codigo="LOTE-2024-SENEPOL-C",
            lote_origem="Agropecuária Vale Verde / GO",
            data_chegada=dt_chegada_3,
            quantidade_cabecas=52,
            peso_chegada_medio=285.0,
            peso_chegada_total=285.0 * 52,
            valor_arroba_pago=230.0,
            valor_total_aquisicao=round((285.0 / 30.0) * 52 * 230.0, 2),
            pasto_atual="Pasto 3 - Cercado da Represa",
            raca="Senepol",
            categoria="Novilho",
            status="Ativo",
            data_proximo_manejo=dt_chegada_3 + timedelta(days=90), # Faltam 10 dias
            observacoes="Manejo de pesagem agendado para a próxima semana."
        )
        db.session.add(lote3)

        # Lote 4: Confinamento Terminação Rápida (com 1 ciclo de 3 meses já realizado)
        dt_chegada_4 = hoje - timedelta(days=110)
        dt_manejo_4a = dt_chegada_4 + timedelta(days=88)
        lote4 = Lote(
            codigo="LOTE-2024-CONF-D",
            lote_origem="Fazenda Estrela D'Alva / MT",
            data_chegada=dt_chegada_4,
            quantidade_cabecas=60,
            peso_chegada_medio=380.0,
            peso_chegada_total=380.0 * 60,
            valor_arroba_pago=228.0,
            valor_total_aquisicao=round((380.0 / 30.0) * 60 * 228.0, 2),
            pasto_atual="Pasto 4 - Confinamento / Curral",
            raca="Anelorado",
            categoria="Boi Gordo / Terminação",
            status="Ativo",
            data_proximo_manejo=dt_manejo_4a + timedelta(days=90),
            observacoes="Dieta com alto teor de concentrado e silagem de milho."
        )
        db.session.add(lote4)
        db.session.flush()

        m4_1 = ManejoTrimestral(
            lote_id=lote4.id,
            ciclo_numero=1,
            data_manejo=dt_manejo_4a,
            dias_desde_ultimo=88,
            peso_anterior_kg=380.0,
            peso_medio_kg=472.0,
            ganho_peso_kg=92.0,
            gmd_kg=round(92.0 / 88, 3),
            arrobas_atual=round(472.0 / 30.0, 2),
            vacinas="Pneumoenterite, Clostridiose",
            remedios="Modificador Orgânico, Suplementação Minerais Quelatados",
            pasto_destino="Pasto 4 - Confinamento / Curral",
            custo_insumos=2200.0,
            observacoes="Excelente desempenho no confinamento com GMD superior a 1 kg/dia."
        )
        db.session.add(m4_1)

        db.session.commit()

        # Gerar uma planilha histórica consolidada salva
        print("Gerando histórico inicial de planilhas salvas...")
        exports_folder = app.config.get('EXPORTS_FOLDER')
        os.makedirs(exports_folder, exist_ok=True)
        
        todos_lotes = Lote.query.all()
        stream = gerar_planilha_consolidada(
            lotes=todos_lotes,
            pastos=pastos,
            titulo_relatorio="Consolidação Trimestral - 1º Trimestre (Histórico Inicial)"
        )
        
        nome_arq = "Planilha_Trimestral_2024-T1_Consolidado.xlsx"
        caminho_arq = os.path.join(exports_folder, nome_arq)
        with open(caminho_arq, 'wb') as f:
            f.write(stream.getvalue())

        planilha1 = PlanilhaConsolidada(
            titulo="Fechamento do 1º Trimestre - Desempenho e Pesagens",
            periodo_referencia="2024-T1",
            tipo_periodo="Trimestral",
            total_lotes=len(todos_lotes),
            total_cabecas=sum(l.quantidade_cabecas for l in todos_lotes),
            peso_medio_rebanho=385.0,
            ganho_medio_kg=45.5,
            investimento_total_rebanho=sum(l.valor_total_aquisicao for l in todos_lotes),
            nome_arquivo=nome_arq,
            observacoes="Consolidação oficial do primeiro trimestre da fazenda com cálculos de @ e GMD."
        )
        db.session.add(planilha1)
        db.session.commit()

        print("Base de dados populada com sucesso!")
        print(f"Total de lotes: {len(todos_lotes)}")
        print(f"Total de cabeças: {sum(l.quantidade_cabecas for l in todos_lotes)}")

if __name__ == '__main__':
    popular_banco()

