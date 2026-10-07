import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fazenda-pecuaria-secret-key-2024-segura')
    
    # Suporte a SQLite persistente local ou PostgreSQL na nuvem
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = database_url or f"sqlite:///{os.path.join(BASE_DIR, 'fazenda.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pasta para salvar planilhas exportadas e backups
    EXPORTS_FOLDER = os.path.join(BASE_DIR, 'exports')
    
    # Configurações do negócio
    PESO_ARROBA_KG = 30.0  # 1 arroba (@) = 30 kg vivo (considerando rendimento de 50% = 15kg de carcaça)
    DIAS_CICLO_MANEJO = 90 # 3 meses de intervalo operacional

