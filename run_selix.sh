#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "🚀 SELIX v4.0 - Inicializando sistema (sem fallbacks)"

if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi
source venv/bin/activate

# Instala dependências
pip install -r requirements.txt

# Cria diretórios
mkdir -p logs

# Mata processos antigos
pkill -f worker_v4 || true
pkill -f main_v4 || true

# Define PYTHONPATH para garantir importações
export PYTHONPATH="/root/selix:$PYTHONPATH"
export REQUESTS_CA_BUNDLE="/root/selix/venv/lib/python3.13/site-packages/certifi/cacert.pem"

# Inicia worker em background (usando -m)
nohup python -m src.selix.worker_v4 > logs/worker.log 2>&1 &
echo "🔄 Worker iniciado (PID $!)"

sleep 3

# Inicia API em foreground (usando -m)
echo "🌐 Iniciando API na porta 5000..."
python -m src.api.main_v4
