from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PastoCercado(db.Model):
    """
    Representa os pastos e cercados da fazenda.
    Permite controlar a taxa de lotação e rotação de pastagem.
    """
    __tablename__ = 'pastos_cercados'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    capacidade_cabecas = db.Column(db.Integer, default=50)
    area_hectares = db.Column(db.Float, default=10.0)
    tipo_pasto = db.Column(db.String(100), default='Brachiaria Brizantha')
    status = db.Column(db.String(30), default='Ativo')  # Ativo, Descanso, Reforma
    observacoes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'capacidade_cabecas': self.capacidade_cabecas,
            'area_hectares': self.area_hectares,
            'tipo_pasto': self.tipo_pasto,
            'status': self.status,
            'observacoes': self.observacoes
        }


class Lote(db.Model):
    """
    Representa um lote de gado na fazenda.
    Armazena os dados de entrada/compra e o estado atual.
    """
    __tablename__ = 'lotes'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(60), nullable=False, unique=True, index=True)
    lote_origem = db.Column(db.String(120), nullable=False)  # Fornecedor/Fazenda de origem
    data_chegada = db.Column(db.Date, nullable=False, default=date.today)
    quantidade_cabecas = db.Column(db.Integer, nullable=False, default=1)
    
    # Pesos e Valores de Entrada
    peso_chegada_medio = db.Column(db.Float, nullable=False)  # kg por animal
    peso_chegada_total = db.Column(db.Float, nullable=False)  # kg total do lote
    valor_arroba_pago = db.Column(db.Float, nullable=False)   # R$ pago por arroba (@)
    valor_total_aquisicao = db.Column(db.Float, nullable=False) # R$ total investido no lote
    
    # Localização e Características
    pasto_atual = db.Column(db.String(100), nullable=False)  # Pasto/Cercado onde estão
    raca = db.Column(db.String(60), default='Nelore')
    categoria = db.Column(db.String(60), default='Boi Magro') # Garrote, Novilho, Boi Magro, Bezerro
    status = db.Column(db.String(30), default='Ativo')        # Ativo, Finalizado, Vendido
    
    # Ciclo Operacional
    data_proximo_manejo = db.Column(db.Date, nullable=False) # Data estimada do próximo ciclo (3 meses)
    observacoes = db.Column(db.Text, nullable=True)
    
    criado_em = db.Column(db.DateTime, default=datetime.now)
    atualizado_em = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relacionamento com os Ciclos de Manejo Trimestrais
    manejos = db.relationship(
        'ManejoTrimestral',
        backref='lote',
        cascade='all, delete-orphan',
        order_by='ManejoTrimestral.data_manejo.asc()'
    )

    @property
    def peso_atual_medio(self):
        """Retorna o peso médio mais recente do lote."""
        if self.manejos and len(self.manejos) > 0:
            return self.manejos[-1].peso_medio_kg
        return self.peso_chegada_medio

    @property
    def peso_atual_total(self):
        """Peso total estimado do lote atualmente."""
        return round(self.peso_atual_medio * self.quantidade_cabecas, 2)

    @property
    def arrobas_chegada_unitario(self):
        """Quantidade de arrobas por animal na entrada (base 30kg vivo = 1@)."""
        return round(self.peso_chegada_medio / 30.0, 2)

    @property
    def arrobas_atuais_unitario(self):
        """Quantidade de arrobas por animal atualmente."""
        return round(self.peso_atual_medio / 30.0, 2)

    @property
    def arrobas_atuais_totais(self):
        """Total de arrobas do lote atualmente."""
        return round(self.arrobas_atuais_unitario * self.quantidade_cabecas, 2)

    @property
    def ganho_peso_total_acumulado(self):
        """Ganho de peso acumulado desde a chegada (kg/animal)."""
        return round(self.peso_atual_medio - self.peso_chegada_medio, 2)

    @property
    def ganho_arrobas_total_acumulado(self):
        """Ganho total em arrobas por animal desde a chegada."""
        return round(self.ganho_peso_total_acumulado / 30.0, 2)

    @property
    def total_ciclos_realizados(self):
        """Quantidade de manejos trimestrais realizados."""
        return len(self.manejos)

    @property
    def dias_na_fazenda(self):
        """Total de dias desde a data de chegada."""
        return (date.today() - self.data_chegada).days

    @property
    def gmd_acumulado(self):
        """Ganho Médio Diário (kg/dia) desde a chegada."""
        dias = self.dias_na_fazenda
        if dias <= 0:
            return 0.0
        return round(self.ganho_peso_total_acumulado / dias, 3)

    @property
    def status_manejo(self):
        """
        Calcula a situação do ciclo trimestral:
        - Atrasado: data prevista já passou
        - Próximo: falta 15 dias ou menos
        - Em dia: faltam mais de 15 dias
        """
        hoje = date.today()
        if not self.data_proximo_manejo:
            return {'status': 'Indefinido', 'dias': 0, 'classe': 'bg-gray-100 text-gray-700'}
        
        dias_restantes = (self.data_proximo_manejo - hoje).days
        if dias_restantes < 0:
            return {
                'status': 'Atrasado',
                'dias': abs(dias_restantes),
                'texto': f'Atrasado há {abs(dias_restantes)} dias',
                'classe': 'bg-red-100 text-red-800 border-red-300'
            }
        elif dias_restantes <= 15:
            return {
                'status': 'Próximo',
                'dias': dias_restantes,
                'texto': f'Em {dias_restantes} dias',
                'classe': 'bg-amber-100 text-amber-800 border-amber-300'
            }
        else:
            return {
                'status': 'Em dia',
                'dias': dias_restantes,
                'texto': f'Faltam {dias_restantes} dias',
                'classe': 'bg-emerald-100 text-emerald-800 border-emerald-300'
            }

    def recalcular_proximo_manejo(self):
        """Calcula a data do próximo manejo com base no último evento + 90 dias."""
        base_data = self.data_chegada
        if self.manejos and len(self.manejos) > 0:
            base_data = self.manejos[-1].data_manejo
        self.data_proximo_manejo = base_data + timedelta(days=90)


class ManejoTrimestral(db.Model):
    """
    Representa o Ciclo de Manejo Trimestral (a cada 3 meses).
    Inclui pesagem, vacinas, remédios e avaliação de ganho zootécnico.
    """
    __tablename__ = 'manejos_trimestrais'

    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.Integer, db.ForeignKey('lotes.id'), nullable=False, index=True)
    
    ciclo_numero = db.Column(db.Integer, nullable=False, default=1) # 1º Ciclo (3 meses), 2º Ciclo (6 meses)...
    data_manejo = db.Column(db.Date, nullable=False, default=date.today)
    dias_desde_ultimo = db.Column(db.Integer, default=90) # Dias decorridos no ciclo
    
    # Pesagem
    peso_medio_kg = db.Column(db.Float, nullable=False)     # Peso aferido neste manejo
    peso_anterior_kg = db.Column(db.Float, nullable=False)  # Peso de referência anterior
    ganho_peso_kg = db.Column(db.Float, nullable=False)     # Ganho líquido no período
    gmd_kg = db.Column(db.Float, default=0.0)               # Ganho Médio Diário no ciclo
    arrobas_atual = db.Column(db.Float, default=0.0)        # @ atual (base 30kg)
    
    # Sanitário & Farmácia
    vacinas = db.Column(db.String(255), nullable=True)      # Ex: Aftosa, Clostridiose, Raiva
    remedios = db.Column(db.String(255), nullable=True)     # Ex: Ivermectina 3.5%, Suplemento ADE
    
    # Manejo de Pastagem
    pasto_destino = db.Column(db.String(100), nullable=False) # Pasto onde continuará ou foi movido
    custo_insumos = db.Column(db.Float, default=0.0)          # Custo total de vacinas/remédios no lote (R$)
    observacoes = db.Column(db.Text, nullable=True)
    
    criado_em = db.Column(db.DateTime, default=datetime.now)

    @property
    def ganho_arrobas(self):
        """Ganho de arrobas no período."""
        return round(self.ganho_peso_kg / 30.0, 2)


class PlanilhaConsolidada(db.Model):
    """
    Registro histórico de planilhas consolidadas mensais e trimestrais.
    Garante rastreabilidade e impede perda de dados ou retrabalho de consolidação.
    """
    __tablename__ = 'planilhas_consolidadas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    periodo_referencia = db.Column(db.String(50), nullable=False) # Ex: 2024-T1, 2024-03
    tipo_periodo = db.Column(db.String(30), default='Trimestral') # Trimestral ou Mensal
    data_geracao = db.Column(db.DateTime, default=datetime.now)
    
    # Totais consolidados
    total_lotes = db.Column(db.Integer, default=0)
    total_cabecas = db.Column(db.Integer, default=0)
    peso_medio_rebanho = db.Column(db.Float, default=0.0)
    ganho_medio_kg = db.Column(db.Float, default=0.0)
    investimento_total_rebanho = db.Column(db.Float, default=0.0)
    
    # Nome do arquivo gerado em disco
    nome_arquivo = db.Column(db.String(255), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
