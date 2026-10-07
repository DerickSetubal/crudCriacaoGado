// Inicialização dos Gráficos Interativos da Dashboard AgroGestão

document.addEventListener('DOMContentLoaded', () => {
    carregarGraficosDashboard();
});

function carregarGraficosDashboard() {
    fetch('/api/dados-graficos')
        .then(res => res.json())
        .then(dados => {
            renderizarGraficoEvolucao(dados.evolucao_peso);
            renderizarGraficoPastos(dados.distribuicao_pastos);
            renderizarGraficoFinanceiro(dados.financeiro_arrobas);
        })
        .catch(err => {
            console.error("Erro ao carregar dados dos gráficos da dashboard:", err);
        });
}

function renderizarGraficoEvolucao(data) {
    const ctx = document.getElementById('chartEvolucaoPeso');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Peso de Entrada (kg)',
                    data: data.pesos_entrada,
                    backgroundColor: '#94a3b8',
                    borderRadius: 6,
                    borderSkipped: false
                },
                {
                    label: 'Peso Atual Médio (kg)',
                    data: data.pesos_atuais,
                    backgroundColor: '#1b4d3e',
                    borderRadius: 6,
                    borderSkipped: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { font: { family: 'Inter', size: 12, weight: '500' } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw.toLocaleString('pt-BR')} kg`;
                        },
                        afterLabel: function(context) {
                            if (context.datasetIndex === 1) {
                                const idx = context.dataIndex;
                                const ganho = data.ganhos[idx];
                                return `Ganho Acumulado: +${ganho.toLocaleString('pt-BR')} kg`;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        callback: val => `${val} kg`,
                        font: { family: 'Inter' }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Inter' } }
                }
            }
        }
    });
}

function renderizarGraficoPastos(data) {
    const ctx = document.getElementById('chartDistribuicaoPastos');
    if (!ctx) return;

    const cores = ['#1b4d3e', '#2d6a4f', '#40916c', '#52b788', '#74c69d', '#95d5b2', '#b7e4c7'];

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.valores,
                backgroundColor: cores.slice(0, data.labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        font: { family: 'Inter', size: 11 },
                        padding: 12
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw;
                            return ` ${context.label}: ${val} cabeças`;
                        }
                    }
                }
            }
        }
    });
}

function renderizarGraficoFinanceiro(data) {
    const ctx = document.getElementById('chartFinanceiroArrobas');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Total Arrobas Atuais (@)',
                    data: data.arrobas,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.3,
                    yAxisID: 'yArrobas',
                    pointRadius: 4,
                    pointBackgroundColor: '#10b981'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { font: { family: 'Inter', size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` Total: ${context.raw.toLocaleString('pt-BR', {minimumFractionDigits: 1})} @`;
                        }
                    }
                }
            },
            scales: {
                yArrobas: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        callback: val => `${val} @`,
                        font: { family: 'Inter' }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Inter' } }
                }
            }
        }
    });
}

