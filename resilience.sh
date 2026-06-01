#!/bin/bash
# SELIX Resilience - Monitor com tolerância de 20min e reinicialização apenas por processo/API

LOG="/root/selix/logs/resilience.log"
STATE_DIR="/root/selix/state"
MAX_RETRIES=3
RETRY_COUNT=0

mkdir -p "$STATE_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

check_api() {
    curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/v1/health | grep -q "200"
}

check_worker_process() {
    pgrep -f "worker_v4" > /dev/null
}

check_data_freshness() {
    local last_ts=$(sqlite3 /root/selix/selix.db "SELECT julianday('now') - julianday(criado_em) FROM commodities ORDER BY criado_em DESC LIMIT 1;" 2>/dev/null)
    if [[ -z "$last_ts" ]]; then
        return 1
    fi
    # converte dias para minutos e compara com 20
    if (( $(echo "$last_ts * 1440 < 20" | bc -l) )); then
        return 0
    else
        return 1
    fi
}

while true; do
    api_ok=false
    worker_ok=false
    data_ok=false

    check_api && api_ok=true
    check_worker_process && worker_ok=true
    check_data_freshness && data_ok=true

    # Apenas loga se os dados estiverem desatualizados, mas não reinicia
    if ! $data_ok; then
        log "⚠️ Dados desatualizados (último Brent > 20 min)"
    fi

    if ! $api_ok || ! $worker_ok; then
        log "⚠️ Problema: API=$api_ok Worker=$worker_ok (ignorando frescor dos dados)"
        if [[ -f "$STATE_DIR/last_ok" ]]; then
            last_ok=$(cat "$STATE_DIR/last_ok")
            now=$(date +%s)
            downtime=$((now - last_ok))
            log "📉 Downtime: ${downtime}s ($((downtime/60))min)"
        fi

        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [[ $RETRY_COUNT -le $MAX_RETRIES ]]; then
            log "🚨 Tentativa $RETRY_COUNT de reinicialização"
            /root/selix/run_selix.sh
            sleep 10
        else
            log "🛑 Máximo de tentativas. Aguardando 5min..."
            sleep 300
            RETRY_COUNT=0
        fi
    else
        RETRY_COUNT=0
        date +%s > "$STATE_DIR/last_ok"
    fi

    sleep 30
done
