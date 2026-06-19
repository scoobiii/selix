#!/bin/bash
# Watchdog para reiniciar a API se cair

cd ~/selix
source venv/bin/activate

while true; do
    if ! curl -s http://localhost:5000/v1/health >/dev/null 2>&1; then
        echo "$(date) - API caiu! Reiniciando..."
        pkill -f main_v4_hmac
        python src/api/main_v4_hmac.py &
        sleep 5
    fi
    sleep 30
done
