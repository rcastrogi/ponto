// ============================================
// Piticas Ponto - JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function () {

    // ------------------------------------------
    // Real-time Clock
    // ------------------------------------------
    const relogioEl = document.getElementById('relogio');
    if (relogioEl) {
        function atualizarRelogio() {
            const agora = new Date();
            const horas = String(agora.getHours()).padStart(2, '0');
            const minutos = String(agora.getMinutes()).padStart(2, '0');
            const segundos = String(agora.getSeconds()).padStart(2, '0');
            relogioEl.textContent = `${horas}:${minutos}:${segundos}`;
        }
        atualizarRelogio();
        setInterval(atualizarRelogio, 1000);
    }

    // ------------------------------------------
    // Punch confirmation
    // ------------------------------------------
    const btnPonto = document.getElementById('btnPonto');
    if (btnPonto) {
        btnPonto.closest('form').addEventListener('submit', function (e) {
            const tipo = btnPonto.textContent.trim();
            if (!confirm(`Confirmar registro de "${tipo}"?`)) {
                e.preventDefault();
            }
        });
    }

    // ------------------------------------------
    // Auto-dismiss alerts after 5 seconds
    // ------------------------------------------
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // ------------------------------------------
    // Date validation for justificativas
    // ------------------------------------------
    const dataInicio = document.getElementById('data_inicio');
    const dataFim = document.getElementById('data_fim');
    if (dataInicio && dataFim) {
        dataInicio.addEventListener('change', function () {
            dataFim.min = dataInicio.value;
            if (dataFim.value && dataFim.value < dataInicio.value) {
                dataFim.value = dataInicio.value;
            }
        });
    }

    // ------------------------------------------
    // Password confirmation
    // ------------------------------------------
    const novaSenha = document.getElementById('nova_senha');
    const confirmarSenha = document.getElementById('confirmar_senha');
    if (novaSenha && confirmarSenha) {
        confirmarSenha.addEventListener('input', function () {
            if (confirmarSenha.value !== novaSenha.value) {
                confirmarSenha.setCustomValidity('As senhas não conferem.');
            } else {
                confirmarSenha.setCustomValidity('');
            }
        });
    }

    // ------------------------------------------
    // Tooltips
    // ------------------------------------------
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });
});
