#!/bin/bash
# Watchdog SELIX - Monitora e reinicia worker automaticamente

LOG_FILE="/root/selix/watchdog.log"
WORKER_SCRIPT="/root/selix/worker_v7.py"
VENV_PATH="/root/selix/venv/bin/python3"
CHECK_INTERVAL=300  # 5 minutos (não 30 segundos!)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🐕 Watchdog SELIX iniciado (PID: $$)"

while true; do
    # Verificar se worker está rodando
    if ! pgrep -f "worker_v7.py" > /dev/null; then
        log "⚠️ Worker não encontrado. Reiniciando..."
        
        cd /root/selix
        source venv/bin/activate
        
        # Iniciar worker em background
        nohup $VENV_PATH $WORKER_SCRIPT >> /root/selix/logs/worker_v7.log 2>&1 &        WORKER_PID=$!
        
        log "✅ Worker reiniciado (PID: $WORKER_PID)"
        sleep 10  # Aguardar um pouco antes de verificar novamente
    else
        # Worker está rodando, verificar último post
        LAST_POST_TIME=$(python3 -c "
import requests
from datetime import datetime, timezone
try:
    url = 'https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed'
    resp = requests.get(url, params={'actor': 'zeh-sobrinho.bsky.social', 'limit': 1}, timeout=10)
    data = resp.json()
    if 'feed' in data and data['feed']:
        created = data['feed'][0]['post']['record']['createdAt']
        post_time = datetime.fromisoformat(created.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff_hours = (now - post_time).total_seconds() / 3600
        print(f'{diff_hours:.1f}')
    else:
        print('999')
except:
    print('999')
" 2>/dev/null)
        
        # Se passou mais de 6h sem postar
        if (( $(echo "$LAST_POST_TIME > 6" | bc -l 2>/dev/null || echo 0) )); then
            log "🚨 ALERTA: $LAST_POST_TIME horas sem postar!"
        else
            log "✅ Worker saudável - último post: ${LAST_POST_TIME}h atrás"
        fi
    fi
    
    # Aguardar intervalo definido
    sleep $CHECK_INTERVAL
done
