# 🐂 AgroGestão - Sistema Web de Gestão Pecuária e Manejo de Gado

Sistema web completo desenvolvido para **gestão, controle e rastreabilidade zootécnica de lotes de gado de corte em fazendas**, eliminando o grave problema de retrabalho com planilhas manuais e garantindo alta eficiência operacional.

---

## 🌾 Contexto do Negócio e Solução Operacional

O ciclo produtivo da pecuária exige precisão no cadastro e monitoramento zootécnico:
1. **Entrada do Lote:** Registro da data de chegada, lote/origem (fornecedor), quantidade de cabeças, peso de chegada, valor pago por arroba (@) e pasto/cercado de alocação.
2. **Ciclo de Manejo Trimestral (a cada 3 meses):** O rebanho passa periodicamente por **pesagem, vacinação e aplicação de medicamentos**. O sistema recupera automaticamente os dados da pesagem anterior, calcula o Ganho de Peso Líquido, Ganho em Arrobas e o **GMD (Ganho Médio Diário)**, agendando o próximo ciclo para 90 dias.
3. **Eliminação do Retrabalho:** Elimina planilhas soltas e erros de digitação através de auto-preenchimento, cálculos em tempo real no formulário, alertas visuais de lotes com manejo pendente e geração de relatórios oficiais em Excel com fórmulas nativas (`=SOMA` e `=MÉDIA`).

---

## 🚀 Funcionalidades Principais

### 1. 📊 Dashboard Interativa & Indicadores (KPIs)
- **KPIs em Tempo Real:** Total de animais ativos, lotes ativos, peso médio do rebanho (kg), ganho médio acumulado por cabeça, volume de arrobas (@ vivas) e custo total investido em aquisição (R$).
- **Alertas de Manejo Trimestral:** Identificação visual inteligente de lotes com manejo **Atrasado** ou **Próximo (nos próximos 15 dias)** com atalho direto de 1 clique para registro no curral.
- **Gráficos Visuais com Chart.js:**
  - *Evolução de Peso dos Lotes:* Comparativo visual do peso de entrada vs. peso atual aferido nos ciclos de manejo.
  - *Distribuição por Pasto/Cercado:* Taxa de ocupação e cabeças por piquete.
  - *Rendimento em Arrobas (@):* Volume total de arrobas produzidas por lote.
- **Tabela de Atividades Recentes:** Histórico das últimas pesagens, vacinas e remédios aplicados.

### 2. 📋 Módulo de Controle de Lotes (CRUD)
- Formulário intuitivo com **simulador e calculadora zootécnica em tempo real**: enquanto o operador digita o peso e o valor da arroba, o sistema calcula instantaneamente o peso total do lote, arrobas por cabeça, custo por animal e investimento total.
- Validação contra códigos duplicados e campos obrigatórios.
- Tabela dinâmica com **filtros instantâneos** por termo de busca (código, origem, raça), pasto/cercado e status.
- **Ficha Completa do Lote:** Linha do tempo visual detalhando desde a data de chegada até todos os manejos trimestrais realizados, mostrando evolução de ganho de peso, GMD e sanitário.
- Ações rápidas de visualização, edição, registro de ciclo e exclusão com modal de confirmação.

### 3. 💉 Módulo de Ciclo de Manejo Trimestral (3 Meses)
- Seleção de lote com **auto-carregamento dinâmico sem retrabalho**: busca automaticamente a pesagem anterior e a data do último manejo.
- Cálculo em tempo real do ganho de peso no período (+kg), ganho em arrobas (+@) e Ganho Médio Diário (**GMD em kg/dia**).
- Seleção rápida com checkboxes para vacinas obrigatórias (*Febre Aftosa, Clostridiose, Raiva, Brucelose*) e medicamentos (*Ivermectina 3.5%, Complexo Vitamínico ADE, Vermífugos, Pour-on*).
- Gestão de rotação de pastagem (possibilidade de mover o lote para outro cercado).
- Reagendamento automático da próxima pesagem para +90 dias.

### 4. 📁 Módulo de Planilhas Salvas & Histórico Consolidado
- **Repositório Centralizado de Fechamentos:** Seção dedicada onde ficam armazenadas as planilhas consolidadas por mês ou trimestre (ex: `2024-T1`, `2024-T2`, etc.), eliminando a necessidade de refazer arquivos antigos.
- **Exportação Instantânea em Excel (`.xlsx`) com o "Melhor Modelo de Dados":**
  - **Aba 1 (Resumo Executivo):** Cabeçalho profissional agro-tech, cards de KPIs e quadro consolidado do rebanho.
  - **Aba 2 (Lotes de Gado):** Tabela completa com código, origem, data de entrada, cabeças, pasto, peso de entrada, valor da @, peso atual, ganho acumulado e **fórmulas nativas do Excel (`=SUM`, `=AVERAGE`)**.
  - **Aba 3 (Histórico de Manejos):** Detalhamento de todas as repesagens trimestrais, vacinas e remédios com médias calculadas.
  - **Aba 4 (Pastos & Cercados):** Distribuição de lotação animal por hectare e status dos piquetes.
  - Formatação profissional de moedas (`R$ #,##0.00`), pesos (`0.0 kg`) e datas (`DD/MM/AAAA`).

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.12, Flask 3.1, Flask-SQLAlchemy 3.1.
- **Banco de Dados:** SQLite (leve, portátil e sem necessidade de configuração externa de servidor).
- **Planilhas & Relatórios:** `openpyxl` (geração de workbooks multi-abas com estilos e fórmulas).
- **Frontend & UI/UX:** HTML5, CSS3, Tailwind CSS (estilo moderno agro-tech em tons de verde floresta, esmeralda e ardósia), Font Awesome 6 (ícones operacionais) e Vanilla JavaScript responsivo.
- **Visualização de Dados:** Chart.js 4 (gráficos de barras, rosca e linhas com animação).

---

## 📂 Estrutura de Arquivos

```
crudCriacaoGado/
│
├── app.py                   # Factory da aplicação Flask e filtros de formatação
├── config.py                # Configurações do sistema e do banco SQLite
├── models.py                # Modelos SQLAlchemy (Lote, ManejoTrimestral, PastoCercado, PlanilhaConsolidada)
├── run.py                   # Script de inicialização do servidor web
├── seed_data.py             # Script com dados de demonstração realistas da fazenda
├── test_app.py              # Bateria de testes unitários automatizados
├── requirements.txt         # Dependências do projeto Python
│
├── routes/                  # Camada de controle e rotas HTTP
│   ├── dashboard.py         # Dashboard principal e endpoints JSON dos gráficos
│   ├── lotes.py             # CRUD de controle de gado e entradas de lotes
│   ├── manejos.py           # Gestão do ciclo de manejo trimestral (3 meses)
│   ├── planilhas.py         # Módulo de histórico e downloads em Excel (.xlsx)
│   └── api.py               # APIs de auto-cálculo e consulta assíncrona
│
├── services/                # Regras de negócio e serviços auxiliares
│   ├── calc_service.py      # Cálculos zootécnicos (arrobas, peso total, GMD)
│   └── excel_service.py     # Gerador de planilhas Excel avançadas e estilizadas
│
├── templates/               # Camada de visualização (Jinja2 + Tailwind)
│   ├── base.html            # Layout mestre com sidebar agro-tech, topbar e modais
│   ├── dashboard.html       # Painel interativo com KPIs, gráficos e alertas
│   ├── lotes/
│   │   ├── index.html       # Tabela dinâmica de lotes com filtros
│   │   ├── form.html        # Formulário com calculadora em tempo real
│   │   └── detalhe.html     # Ficha completa do lote e linha do tempo de 3 meses
│   ├── manejos/
│   │   ├── index.html       # Histórico geral de manejos trimestrais
│   │   └── novo.html        # Assistente rápido de manejo sem retrabalho
│   └── planilhas/
│       └── index.html       # Repositório de planilhas salvas e exportação
│
├── static/                  # Arquivos estáticos
│   ├── css/custom.css       # Estilos adicionais e micro-animações
│   └── js/
│       ├── main.js          # Reatividade, calculadora em tempo real e modais
│       └── dashboard.js     # Inicialização dos gráficos interativos Chart.js
│
└── exports/                 # Diretório de armazenamento das planilhas Excel arquivadas
```

---

## ⚡ Como Instalar e Rodar o Projeto Localmente

### 1. Pré-requisitos
- Ter o **Python 3.10 ou superior** instalado no computador.

### 2. Passo a Passo de Execução

Abra o terminal (PowerShell ou Bash) na pasta do projeto:

```powershell
# 1. Acesse o diretório do projeto
cd c:\Users\User\crudCriacaoGado

# 2. Crie o ambiente virtual (caso ainda não tenha criado)
python -m venv .venv

# 3. Ative o ambiente virtual
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Ou no Windows (CMD):
.venv\Scripts\activate.bat
# No Linux/Mac:
source .venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Popule o banco com dados de exemplo realistas (Opcional, mas recomendado!)
python seed_data.py

# 6. Inicie o servidor web
python run.py
```

### 3. Acessando o Sistema
Após iniciar o servidor, abra seu navegador de preferência e acesse:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

#### 🔐 Credenciais de Acesso Exclusivo (Login Restrito):
- **Login / Usuário:** `admin.neto`
- **Senha:** `admin123`
*(O sistema possui cadastro público desativado por segurança, permitindo acesso apenas com as credenciais autorizadas).*

---

## 🧪 Como Executar os Testes Automatizados

O sistema inclui uma suíte de testes unitários que valida todas as rotas principais, o cálculo de arrobas, o ciclo de manejo e a geração das planilhas Excel:

```powershell
python test_app.py
```

Você verá a confirmação com todos os testes passando com `OK`:
```
Ran 8 tests in ~0.9s
OK
```

---

## 📐 Regras Zootécnicas e Fórmulas Adotadas

| Indicador | Base de Cálculo | Descrição |
| :--- | :--- | :--- |
| **Arroba Viva (@)** | `Peso Vivo (kg) / 30.0` | 1 @ viva = 30 kg vivos (considera rendimento de carcaça padrão de 50% = 15 kg de carcaça). |
| **Volume Total em @** | `Arroba por Cabeça * Cabeças` | Volume comercializável total do lote. |
| **Investimento de Aquisição** | `Total de Arrobas * Valor da @ Pago` | Custo total desembolsado na compra do lote. |
| **Ganho de Peso do Manejo** | `Peso Atual (kg) - Peso Anterior (kg)` | Ganho líquido de carcaça alcançado no período de 90 dias. |
| **GMD (Ganho Médio Diário)** | `Ganho de Peso (kg) / Dias Decorridos` | Medida de eficiência zootécnica diária da nutrição e manejo no pasto. |
| **Ciclo Operacional** | `Data do Último Manejo + 90 dias` | Intervalo trimestral recomendado para repesagem e profilaxia sanitária. |

---

## 👨‍💻 Padrões de Qualidade e Boas Práticas

- **Arquitetura em Camadas (Separation of Concerns):** Rotas separadas em blueprints temáticos, serviços desacoplados para regras zootécnicas e geração de planilhas.
- **Design UI/UX Limpo e Focado no Produtor:** Alto contraste, botões grandes e claros, ícones intuitivos para uso ágil no campo ou escritório da fazenda.
- **Prevenção de Erros Humanos:** Campos numéricos com validações de mínimo e máximo, cálculos de ganho automáticos e pré-preenchimento inteligente sem retrabalho.
- **Portabilidade:** Funciona de forma autônoma sem dependência de bancos pesados externos, pronto para empacotamento local ou deploy na nuvem.