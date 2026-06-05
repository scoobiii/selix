#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "🚀 SELIX v4.0 - Inicializando sistema (sem fallbacks)"

if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi
source venv/bin/activate

pip install -r requirements.txt
mkdir -p logs

# Mata processos antigos
pkill -f worker_v4 || true
pkill -f main_v4 || true
pkill -f campaign_supervisor || true

export PYTHONPATH="/root/selix:$PYTHONPATH"
export REQUESTS_CA_BUNDLE="/root/selix/venv/lib/python3.13/site-packages/certifi/cacert.pem"

# Worker
nohup python -m src.selix.worker_v4 > logs/worker.log 2>&1 &
echo "🔄 Worker iniciado (PID $!)"

# API
nohup python -m src.api.main_v4 > logs/api.log 2>&1 &
echo "🌐 API iniciada (PID $!)"

# CAMPAIGN SUPERVISOR (posts automáticos) – É O QUE FALTAVA
nohup python scripts/campaign_supervisor.py > logs/supervisor.log 2>&1 &
echo "🤖 Campaign Supervisor iniciado (PID $!)"

echo "✅ Todos os serviços rodando."
echo "📋 Logs: logs/worker.log, logs/api.log, logs/supervisor.log"
