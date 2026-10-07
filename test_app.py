import unittest
from datetime import date
from app import create_app
from models import db, Lote, ManejoTrimestral, PastoCercado, PlanilhaConsolidada
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class TestSistemaPecuaria(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            lote = Lote(
                codigo='LOTE-TESTE-INIT',
                lote_origem='Fazenda Modelo',
                data_chegada=date.today(),
                quantidade_cabecas=20,
                peso_chegada_medio=300.0,
                peso_chegada_total=6000.0,
                valor_arroba_pago=230.0,
                valor_total_aquisicao=46000.0,
                pasto_atual='Pasto 1 - Braquiária Sul',
                raca='Nelore',
                categoria='Boi Magro',
                status='Ativo',
                data_proximo_manejo=date.today()
            )
            db.session.add(lote)
            db.session.commit()

    def autenticar(self):
        """Helper para autenticar o cliente nos testes."""
        with self.client.session_transaction() as sess:
            sess['autenticado'] = True
            sess['usuario'] = 'admin.neto'

    def test_bloqueio_sem_login(self):
        """Testa que rotas internas redirecionam para /login se não autenticado."""
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location'))

    def test_login_incorreto(self):
        """Testa tentativa de login com credenciais erradas."""
        response = self.client.post('/login', data={'usuario': 'errado', 'senha': '123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Usu\xc3\xa1rio ou senha incorretos', response.data)

    def test_login_sucesso(self):
        """Testa login com sucesso usando admin.neto e admin123."""
        response = self.client.post('/login', data={'usuario': 'admin.neto', 'senha': 'admin123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel de Desempenho', response.data)

    def test_dashboard_status(self):
        """Testa carregamento da dashboard principal autenticada."""
        self.autenticar()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Painel de Desempenho', response.data)
        self.assertIn(b'admin.neto', response.data)

    def test_lotes_listagem(self):
        """Testa listagem de lotes autenticada."""
        self.autenticar()
        response = self.client.get('/lotes/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Controle de Lotes de Gado', response.data)

    def test_cadastrar_novo_lote(self):
        """Testa o cadastro de um novo lote de gado."""
        self.autenticar()
        payload = {
            'codigo': 'LOTE-TESTE-99',
            'lote_origem': 'Fazenda Teste Agro',
            'data_chegada': str(date.today()),
            'quantidade_cabecas': '25',
            'peso_chegada_medio': '340.0',
            'valor_arroba_pago': '240.00',
            'pasto_atual': 'Pasto 1 - Braquiária Sul',
            'raca': 'Nelore',
            'categoria': 'Boi Magro',
            'observacoes': 'Teste unitário automatizado'
        }
        response = self.client.post('/lotes/novo', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOTE-TESTE-99', response.data)

    def test_detalhe_lote(self):
        """Testa a visualização da ficha completa do lote."""
        self.autenticar()
        with self.app.app_context():
            lote = Lote.query.first()
            self.assertIsNotNone(lote)
            lote_id = lote.id

        response = self.client.get(f'/lotes/{lote_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Evolu', response.data)

    def test_registrar_manejo_trimestral(self):
        """Testa o registro de ciclo de 3 meses."""
        self.autenticar()
        with self.app.app_context():
            lote = Lote.query.first()
            lote_id = lote.id

        payload = {
            'lote_id': str(lote_id),
            'peso_medio_kg': '410.0',
            'data_manejo': str(date.today()),
            'pasto_destino': 'Pasto 2 - Piquete Mombaça',
            'vacinas_padrao': ['Febre Aftosa', 'Clostridiose (Poli-Star)'],
            'outras_vacinas': '',
            'remedios_padrao': ['Ivermectina 3.5%'],
            'outros_remedios': '',
            'custo_insumos': '950.0',
            'observacoes': 'Manejo trimestral realizado com sucesso'
        }
        response = self.client.post('/manejos/novo', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ciclo de manejo', response.data)

    def test_exportar_excel_atual(self):
        """Testa geração e download da planilha Excel com os dados consolidados."""
        self.autenticar()
        response = self.client.get('/planilhas/exportar-atual')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('Content-Type'),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_planilhas_historico(self):
        """Testa visualização do módulo de planilhas salvas."""
        self.autenticar()
        response = self.client.get('/planilhas/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hist', response.data)
        self.assertIn(b'Reposit', response.data)

if __name__ == '__main__':
    unittest.main()
