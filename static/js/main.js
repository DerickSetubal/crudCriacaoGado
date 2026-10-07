// Utilitários de Interface e Reatividade - AgroGestão Pecuária

document.addEventListener('DOMContentLoaded', () => {
    // 1. Feedback visual imediato nos botões de submissão
    const forms = document.querySelectorAll('form[data-loading-feedback]');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('btn-loading');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = `
                    <span class="inline-flex items-center gap-2">
                        <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Salvando dados...
                    </span>
                `;
            }
        });
    });

    // 2. Auto-cálculo em tempo real no formulário de Lote (Entrada)
    inicializarCalculadoraLote();

    // 3. Auto-cálculo e carregamento dinâmico no formulário de Manejo Trimestral
    inicializarFormularioManejo();
});

// Formatadores auxiliares
function formatarMoeda(val) {
    return Number(val).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarNumero(val, casas = 1) {
    return Number(val).toLocaleString('pt-BR', { minimumFractionDigits: casas, maximumFractionDigits: casas });
}

// =========================================================================
// Calculadora em Tempo Real: Entrada de Lote
// =========================================================================
function inicializarCalculadoraLote() {
    const inputPeso = document.getElementById('peso_chegada_medio');
    const inputQtd = document.getElementById('quantidade_cabecas');
    const inputValorArr = document.getElementById('valor_arroba_pago');

    if (!inputPeso || !inputQtd || !inputValorArr) return;

    function recalcular() {
        const pesoMedio = parseFloat(inputPeso.value) || 0;
        const qtd = parseInt(inputQtd.value) || 0;
        const valorArr = parseFloat(inputValorArr.value) || 0;

        const pesoTotal = pesoMedio * qtd;
        const arrobasPorCabeca = pesoMedio > 0 ? (pesoMedio / 30.0) : 0;
        const totalArrobas = arrobasPorCabeca * qtd;
        const custoPorCabeca = arrobasPorCabeca * valorArr;
        const custoTotal = totalArrobas * valorArr;

        // Atualizar os elementos da UI de resumo lateral
        const elPesoTotal = document.getElementById('calc_peso_total');
        const elArrCabeca = document.getElementById('calc_arr_cabeca');
        const elTotalArr = document.getElementById('calc_total_arrobas');
        const elCustoCabeca = document.getElementById('calc_custo_cabeca');
        const elCustoTotal = document.getElementById('calc_custo_total');

        if (elPesoTotal) elPesoTotal.textContent = `${formatarNumero(pesoTotal, 1)} kg`;
        if (elArrCabeca) elArrCabeca.textContent = `${formatarNumero(arrobasPorCabeca, 2)} @`;
        if (elTotalArr) elTotalArr.textContent = `${formatarNumero(totalArrobas, 2)} @`;
        if (elCustoCabeca) elCustoCabeca.textContent = formatarMoeda(custoPorCabeca);
        if (elCustoTotal) elCustoTotal.textContent = formatarMoeda(custoTotal);
    }

    inputPeso.addEventListener('input', recalcular);
    inputQtd.addEventListener('input', recalcular);
    inputValorArr.addEventListener('input', recalcular);

    // Executa uma vez no início
    recalcular();
}

// =========================================================================
// Assistente do Ciclo de Manejo Trimestral (Auto-fill sem retrabalho)
// =========================================================================
function inicializarFormularioManejo() {
    const selectLote = document.getElementById('select_lote_manejo');
    const inputNovoPeso = document.getElementById('peso_medio_kg');
    const inputDataManejo = document.getElementById('data_manejo');

    if (!selectLote || !inputNovoPeso) return;

    let dadosLoteAtual = {
        peso_anterior: 0,
        data_anterior: null,
        pasto_atual: ''
    };

    function carregarDadosDoLote(loteId) {
        if (!loteId) return;

        fetch(`/api/lote/${loteId}/dados-manejo`)
            .then(res => res.json())
            .then(data => {
                dadosLoteAtual.peso_anterior = data.peso_anterior_kg;
                dadosLoteAtual.data_anterior = data.data_anterior;
                dadosLoteAtual.pasto_atual = data.pasto_atual;

                // Atualizar labels informativos
                const elCicloBadge = document.getElementById('badge_ciclo_numero');
                const elPesoAnterior = document.getElementById('info_peso_anterior');
                const elDataAnterior = document.getElementById('info_data_anterior');
                const selectPasto = document.getElementById('pasto_destino');

                if (elCicloBadge) elCicloBadge.textContent = `${data.proximo_ciclo}º Ciclo (3 meses)`;
                if (elPesoAnterior) elPesoAnterior.textContent = `${formatarNumero(data.peso_anterior_kg, 1)} kg`;
                if (elDataAnterior) elDataAnterior.textContent = data.data_anterior_formatada;

                // Pré-selecionar pasto atual
                if (selectPasto && data.pasto_atual) {
                    selectPasto.value = data.pasto_atual;
                }

                recalcularGanhos();
            })
            .catch(err => console.error("Erro ao carregar dados do lote:", err));
    }

    function recalcularGanhos() {
        const novoPeso = parseFloat(inputNovoPeso.value) || 0;
        const pesoAnterior = dadosLoteAtual.peso_anterior || 0;
        const dataManejo = inputDataManejo ? inputDataManejo.value : null;

        if (novoPeso <= 0 || pesoAnterior <= 0) return;

        const ganhoKg = novoPeso - pesoAnterior;
        const ganhoArr = ganhoKg / 30.0;

        let dias = 90;
        if (dadosLoteAtual.data_anterior && dataManejo) {
            const dt1 = new Date(dadosLoteAtual.data_anterior);
            const dt2 = new Date(dataManejo);
            const diffTime = dt2 - dt1;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            if (diffDays > 0) dias = diffDays;
        }

        const gmd = dias > 0 ? (ganhoKg / dias) : 0;

        const elGanhoKg = document.getElementById('calc_ganho_kg');
        const elGanhoArr = document.getElementById('calc_ganho_arr');
        const elGmd = document.getElementById('calc_gmd');
        const elDias = document.getElementById('calc_dias_periodo');

        if (elGanhoKg) {
            const sinal = ganhoKg >= 0 ? '+' : '';
            elGanhoKg.textContent = `${sinal}${formatarNumero(ganhoKg, 1)} kg`;
            elGanhoKg.className = ganhoKg >= 0 ? 'text-2xl font-bold text-emerald-700' : 'text-2xl font-bold text-red-600';
        }
        if (elGanhoArr) {
            const sinal = ganhoArr >= 0 ? '+' : '';
            elGanhoArr.textContent = `${sinal}${formatarNumero(ganhoArr, 2)} @`;
        }
        if (elGmd) {
            elGmd.textContent = `${formatarNumero(gmd, 3)} kg/dia`;
        }
        if (elDias) {
            elDias.textContent = `${dias} dias`;
        }
    }

    selectLote.addEventListener('change', () => {
        carregarDadosDoLote(selectLote.value);
    });

    inputNovoPeso.addEventListener('input', recalcularGanhos);
    if (inputDataManejo) {
        inputDataManejo.addEventListener('change', recalcularGanhos);
    }

    // Se já veio com lote selecionado
    if (selectLote.value) {
        carregarDadosDoLote(selectLote.value);
    }
}

// =========================================================================
// Gerenciador de Modais de Confirmação
// =========================================================================
function abrirModalExclusao(formId, nomeItem) {
    const modal = document.getElementById('modal_confirmacao_exclusao');
    const msg = document.getElementById('modal_mensagem_exclusao');
    const btnConfirmar = document.getElementById('btn_confirmar_exclusao');

    if (!modal) return;

    if (msg) msg.textContent = `Tem certeza que deseja excluir "${nomeItem}"? Esta ação não poderá ser desfeita.`;
    
    btnConfirmar.onclick = () => {
        const form = document.getElementById(formId);
        if (form) form.submit();
    };

    modal.classList.remove('hidden');
}

function fecharModalExclusao() {
    const modal = document.getElementById('modal_confirmacao_exclusao');
    if (modal) modal.classList.add('hidden');
}

