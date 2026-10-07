import os
from datetime import datetime
from flask import Flask
from config import Config
from models import db, PastoCercado

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensões
    db.init_app(app)

    from routes.auth import bp_auth
    from routes.dashboard import bp_dashboard
    from routes.lotes import bp_lotes
    from routes.manejos import bp_manejos
    from routes.planilhas import bp_planilhas
    from routes.api import bp_api

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_lotes)
    app.register_blueprint(bp_manejos)
    app.register_blueprint(bp_planilhas)
    app.register_blueprint(bp_api)

    # Proteção de acesso: redireciona para /login se não autenticado
    @app.before_request
    def verificar_autenticacao():
        from flask import request, session, redirect, url_for
        rotas_livres = ['auth.login', 'static']
        if request.endpoint and any(request.endpoint.startswith(r) for r in rotas_livres):
            return None
        if not session.get('autenticado'):
            return redirect(url_for('auth.login'))

    # Criar pasta de exportações se não existir
    os.makedirs(app.config.get('EXPORTS_FOLDER', 'exports'), exist_ok=True)

    # Filtros personalizados Jinja2 para apresentação visual no padrão brasileiro
    @app.template_filter('moeda')
    def formato_moeda(valor):
        if valor is None:
            return "R$ 0,00"
        try:
            val = float(valor)
            return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return f"R$ {valor}"

    @app.template_filter('peso')
    def formato_peso(valor):
        if valor is None:
            return "0,0 kg"
        try:
            val = float(valor)
            return f"{val:,.1f} kg".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return f"{valor} kg"

    @app.template_filter('data_br')
    def formato_data_br(dt):
        if not dt:
            return "-"
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt, '%Y-%m-%d').date()
            except ValueError:
                return dt
        return dt.strftime('%d/%m/%Y')

    # Variáveis globais para os templates
    @app.context_processor
    def inject_global_data():
        from flask import session
        return {
            'ano_atual': datetime.now().year,
            'agora': datetime.now(),
            'usuario_logado': session.get('usuario')
        }

    # Inicialização do banco de dados e dados essenciais
    with app.app_context():
        db.create_all()
        # Inicializa pastos padrão se não existirem
        if PastoCercado.query.count() == 0:
            pastos_iniciais = [
                PastoCercado(nome="Pasto 1 - Braquiária Sul", capacidade_cabecas=80, area_hectares=18.5, tipo_pasto="Brachiaria brizantha"),
                PastoCercado(nome="Pasto 2 - Piquete Mombaça", capacidade_cabecas=60, area_hectares=12.0, tipo_pasto="Panicum maximum Mombaça"),
                PastoCercado(nome="Pasto 3 - Cercado da Represa", capacidade_cabecas=100, area_hectares=22.0, tipo_pasto="Brachiaria decumbens"),
                PastoCercado(nome="Pasto 4 - Confinamento / Curral", capacidade_cabecas=120, area_hectares=5.0, tipo_pasto="Curral Coberto e Cocho"),
                PastoCercado(nome="Pasto 5 - Piquete Maternidade/Recria", capacidade_cabecas=50, area_hectares=10.0, tipo_pasto="Brachiaria humidicola"),
            ]
            db.session.bulk_save_objects(pastos_iniciais)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

