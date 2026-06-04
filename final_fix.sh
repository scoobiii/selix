#!/bin/bash
# final_fix.sh - Correções finais do SELIX

set -e

cd /root/selix

echo "🔧 CORREÇÕES FINAIS - SELIX"
echo "============================"

# 1. Remover import duplicado
echo "1️⃣ Removendo 'import os' duplicado..."
awk '!seen[$0]++ || !/^import os$/' worker_v7.py > worker_v7_temp.py && mv worker_v7_temp.py worker_v7.py
echo "   ✅ Concluído"

# 2. Parar tudo
echo "2️⃣ Parando processos..."
pkill -f watchdog_selix.sh 2>/dev/null || true
pkill -f worker_v7.py 2>/dev/null || true
sleep 3
echo "   ✅ Processos parados"

# 3. Corrigir watchdog para não reiniciar tão rápido
echo "3️⃣ Ajustando watchdog_selix.sh..."
cat > watchdog_selix.sh << 'WATCHDOG'
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
WATCHDOG

chmod +x watchdog_selix.sh
echo "   ✅ watchdog ajustado (intervalo: 5 minutos)"

# 4. Reiniciar tudo
echo "4️⃣ Reiniciando watchdog..."
nohup ./watchdog_selix.sh > watchdog.log 2>&1 &
WATCHDOG_PID=$!
echo "   ✅ Watchdog iniciado (PID: $WATCHDOG_PID)"

# 5. Aguardar e verificar
sleep 15
echo ""
echo "📊 STATUS FINAL:"
echo "================"
ps aux | grep -E "(watchdog|worker)" | grep -v grep

echo ""
echo "📋 ÚLTIMAS 10 LINHAS DO WATCHDOG:"
tail -10 watchdog.log

echo ""
echo "📋 ÚLTIMAS 10 LINHAS DO WORKER:"
tail -10 logs/worker_v7.log 2>/dev/null || echo "Log não encontrado"

echo ""
echo "✅ Correções finais concluídas!"
