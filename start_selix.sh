#!/bin/bash
# ============================================================
# SELIX ECOSSISTEMA COMPLETO – Worker + API + Watchdog
# ============================================================

cd /root/selix
source venv/bin/activate

# 1. Mata processos antigos
pkill -f worker_final_clean 2>/dev/null
pkill -f main_v4_fixed 2>/dev/null
pkill -f watchdog_daemon 2>/dev/null
pkill -f "python.*5000" 2>/dev/null

# 2. Limpa logs antigos
find logs -name "*.log" -mtime +7 -delete 2>/dev/null

# 3. Inicia o worker
nohup python worker_final_clean.py > logs/worker.log 2>&1 &
WORKER_PID=$!

# 4. Inicia a API
nohup python src/api/main_v4_fixed.py > logs/api.log 2>&1 &
API_PID=$!

# 5. Inicia o watchdog (monitora worker + API)
nohup ./watchdog_daemon.sh > logs/watchdog.log 2>&1 &
WATCHDOG_PID=$!

echo "✅ SELIX iniciado!"
echo "   Worker PID: $WORKER_PID"
echo "   API PID: $API_PID"
echo "   Watchdog PID: $WATCHDOG_PID"
echo "   API: http://localhost:5000/v1/health"
