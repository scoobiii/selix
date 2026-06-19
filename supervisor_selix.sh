#!/bin/bash
# ============================================================
# SELIX SUPERVISOR – Mantém worker e API rodando 24/7
# ============================================================

cd /root/selix
source venv/bin/activate

# Função para verificar se um processo está rodando
is_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Função para iniciar o worker
start_worker() {
    if ! is_running "worker_final_clean.py"; then
        echo "$(date) - 🔄 Reiniciando worker..."
        python worker_final_clean.py &
        echo "$(date) - ✅ Worker iniciado (PID: $!)"
    fi
}

# Função para iniciar a API
start_api() {
    if ! is_running "main_v4_fixed.py"; then
        echo "$(date) - 🔄 Reiniciando API..."
        python src/api/main_v4_fixed.py &
        echo "$(date) - ✅ API iniciada (PID: $!)"
    fi
}

# Loop infinito de supervisão
while true; do
    start_worker
    start_api
    sleep 30
done
