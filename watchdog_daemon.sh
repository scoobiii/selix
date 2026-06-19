#!/bin/bash
# ============================================================
# WATCHDOG – Monitora worker + API e reinicia se cair
# ============================================================

cd /root/selix
source venv/bin/activate

while true; do
    # Verifica worker
    if ! pgrep -f "worker_final_clean.py" > /dev/null; then
        echo "$(date) - Worker caiu! Reiniciando..."
        nohup python worker_final_clean.py > logs/worker.log 2>&1 &
    fi
    
    # Verifica API
    if ! pgrep -f "main_v4_fixed.py" > /dev/null; then
        echo "$(date) - API caiu! Reiniciando..."
        nohup python src/api/main_v4_fixed.py > logs/api.log 2>&1 &
    fi
    
    sleep 30
done
