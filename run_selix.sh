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

# ============================================================
# GERAR DOCUMENTAÇÃO SWAGGER (se o script existir)
# ============================================================
if [ -f "generate_swagger.py" ]; then
    echo "📄 Gerando documentação Swagger (static/swagger.json)..."
    python generate_swagger.py
else
    echo "⚠️  generate_swagger.py não encontrado. Pule geração do Swagger."
fi

# Mata processos antigos
nohup python worker_v7.py > logs/worker.log 2>&1 &
pkill -f main_v4 || true
pkill -f campaign_supervisor || true

export PYTHONPATH="/root/selix:$PYTHONPATH"
export REQUESTS_CA_BUNDLE="/root/selix/venv/lib/python3.13/site-packages/certifi/cacert.pem"

# Worker
nohup python worker_v7.py > logs/worker.log 2>&1 &
echo "🔄 Worker iniciado (PID $!)"

# API
nohup python src/api/main_v4.py > logs/api.log 2>&1 &
echo "🌐 API iniciada (PID $!)"

# Campaign Supervisor
nohup python scripts/campaign_supervisor.py > logs/supervisor.log 2>&1 &
echo "🤖 Campaign Supervisor iniciado (PID $!)"

echo "✅ Todos os serviços rodando."
echo "📋 Logs: logs/worker.log, logs/api.log, logs/supervisor.log"
echo "📖 Documentação Swagger: http://localhost:5000/api/docs"
