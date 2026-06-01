#!/data/data/com.termux/files/usr/bin/bash
# SELIX Resilience – Prevayler-style recovery

LOG="/root/selix/resilience.log"
STATE_DIR="/root/selix/state"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"; }

# Verifica se o processo principal está rodando
check_worker() {
    pgrep -f "worker_v4.py" > /dev/null
    return $?
}

check_api() {
    curl -s http://localhost:5000/v1/health > /dev/null 2>&1
    return $?
}

# Recupera estado do banco
recover_db() {
    if [ -f "$STATE_DIR/selix.db.backup" ]; then
        log "Restaurando banco do backup..."
        cp "$STATE_DIR/selix.db.backup" /root/selix/selix.db
    else
        log "Nenhum backup encontrado"
    fi
}

# Recupera conversas
recover_conversations() {
    if [ -f "$STATE_DIR/selix_state.pkl" ]; then
        log "Ultimo estado: $(python -c "import pickle; print(pickle.load(open('$STATE_DIR/selix_state.pkl', 'rb')).get('last_action', 'N/A'))")"
    fi
}

# Inicia serviços
start_services() {
    cd /root/selix
    source venv/bin/activate
    
    log "Iniciando worker..."
    nohup python src/selix/worker_v4.py >> /root/selix/logs/worker.log 2>&1 &
    WORKER_PID=$!
    
    sleep 3
    log "Iniciando API..."
    nohup python src/api/main_v4.py >> /root/selix/logs/api.log 2>&1 &
    API_PID=$!
    
    log "Servicos iniciados: worker=$WORKER_PID, api=$API_PID"
}

# Loop de monitoramento
while true; do
    if ! check_worker || ! check_api; then
        log "Servico caiu! Recuperando..."
        recover_db
        recover_conversations
        start_services
    fi
    sleep 10
done
