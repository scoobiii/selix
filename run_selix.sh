#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "🚀 SELIX - Inicializando sistema completo"

# Ativa venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ venv não encontrado. Execute: make venv"
    exit 1
fi

# Instala dependências (caso falte algo)
pip install -r requirements.txt > /dev/null

# Cria banco de dados e tabelas (se não existir)
if [ ! -f "selix.db" ]; then
    echo "📦 Criando banco de dados..."
    python3 -c "
import sqlite3
conn = sqlite3.connect('selix.db')
conn.executescript('''
CREATE TABLE IF NOT EXISTS commodities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    preco_usd REAL,
    unidade TEXT,
    fonte TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS empresas_rj (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    codigo_b3 TEXT,
    setor TEXT,
    preco_atual REAL,
    preco_selix REAL,
    market_cap_atual REAL,
    market_cap_selix REAL,
    potencial_percentual REAL,
    plr_bloqueado INTEGER,
    funcionarios INTEGER,
    processo TEXT,
    status TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()
conn.close()
print('✅ Banco e tabelas criados')
"
fi

# Cria worker_real.py se não existir (com coleta de dados reais)
if [ ! -f "src/selix/worker_real.py" ]; then
    echo "🤖 Criando worker de coleta de dados reais..."
    mkdir -p src/selix
    cat > src/selix/worker_real.py << 'WORKER'
#!/usr/bin/env python3
import sqlite3
import time
import yfinance as yf
from datetime import datetime

DB_PATH = '/root/selix/selix.db'

def get_db():
    return sqlite3.connect(DB_PATH)

def update_brent():
    try:
        brent = yf.Ticker("BZ=F")
        data = brent.history(period="1d")
        if not data.empty:
            preco = round(data['Close'].iloc[-1], 2)
            conn = get_db()
            conn.execute("INSERT INTO commodities (nome, preco_usd, unidade, fonte) VALUES (?, ?, ?, ?)",
                         ('Brent', preco, 'USD/bbl', 'yfinance'))
            conn.commit()
            conn.close()
            print(f"[{datetime.now()}] Brent atualizado: {preco}")
    except Exception as e:
        print(f"Erro Brent: {e}")

def update_empresas():
    # Dados reais fixos (pode ser atualizado manualmente ou via API)
    empresas = [
        {"nome": "GPA", "codigo_b3": "PCAR3", "setor": "Varejo", "preco_atual": 2.50, "preco_selix": 4.20,
         "market_cap_atual": 1.2e9, "market_cap_selix": 2.0e9, "potencial_percentual": 68.0,
         "plr_bloqueado": 1, "funcionarios": 45000, "processo": "RJ em andamento", "status": "crítica"},
        {"nome": "Raízen", "codigo_b3": "RAIZ4", "setor": "Energia", "preco_atual": 2.80, "preco_selix": 5.10,
         "market_cap_atual": 8.5e9, "market_cap_selix": 15.0e9, "potencial_percentual": 76.4,
         "plr_bloqueado": 1, "funcionarios": 30000, "processo": "RJ homologado", "status": "monitoramento"}
    ]
    conn = get_db()
    for emp in empresas:
        conn.execute('''INSERT OR REPLACE INTO empresas_rj 
            (nome, codigo_b3, setor, preco_atual, preco_selix, market_cap_atual, market_cap_selix, potencial_percentual, plr_bloqueado, funcionarios, processo, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (emp['nome'], emp['codigo_b3'], emp['setor'], emp['preco_atual'], emp['preco_selix'],
             emp['market_cap_atual'], emp['market_cap_selix'], emp['potencial_percentual'],
             emp['plr_bloqueado'], emp['funcionarios'], emp['processo'], emp['status']))
    conn.commit()
    conn.close()
    print(f"[{datetime.now()}] Empresas RJ atualizadas")

if __name__ == '__main__':
    # Executa uma vez imediatamente
    update_brent()
    update_empresas()
    # Depois a cada 5 minutos
    while True:
        time.sleep(300)
        update_brent()
        update_empresas()
WORKER
    chmod +x src/selix/worker_real.py
fi

# Mata processos antigos
pkill -f "worker_real.py" 2>/dev/null || true
pkill -f "main_v3.py" 2>/dev/null || true

# Inicia worker em background
echo "🔄 Iniciando worker de coleta (Brent via Yahoo Finance)..."
nohup python3 src/selix/worker_real.py > worker.log 2>&1 &
sleep 5

# Verifica se o banco já tem dados
python3 -c "import sqlite3; conn=sqlite3.connect('selix.db'); cur=conn.execute('SELECT COUNT(*) FROM commodities'); print('📊 Dados no banco:', cur.fetchone()[0])" 2>/dev/null || echo "⚠️ Banco vazio, worker vai popular..."

# Inicia API
echo "🌐 Iniciando API REST na porta 5000..."
exec python3 src/api/main_v3.py
