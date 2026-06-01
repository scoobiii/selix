#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "🚀 SELIX v4.0 - Inicializando sistema (sem fallbacks)"

# Ativa venv se existir, senão cria
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

# Inicia worker em background
nohup python src/selix/worker_v4.py > logs/worker.log 2>&1 &
echo "🔄 Worker iniciado (PID $!)"

# Aguarda um pouco e inicia a API
sleep 3
echo "🌐 Iniciando API na porta 5000..."
python src/api/main_v4.py
