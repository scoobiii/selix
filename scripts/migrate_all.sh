#!/bin/bash
# migrate_all.sh - Migração completa do SELIX (ordem correta)

set -e

DB_PATH="/root/selix/selix.db"

echo "🚀 Iniciando migração profissional do SELIX..."
echo "================================================"

# 1. Criar tabelas principais (ORDEM CORRETA)
echo ""
echo "📦 Passo 1/5: Criando tabelas principais..."
sqlite3 "$DB_PATH" << 'SQL'
-- Tabela de commodities (PRECIISA VIR PRIMEIRO)
CREATE TABLE IF NOT EXISTS commodities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    preco_usd REAL NOT NULL,
    unidade TEXT DEFAULT 'USD',
    fonte TEXT,
    criado_em TEXT DEFAULT (datetime('now'))
);

-- Tabela de preços energéticos
CREATE TABLE IF NOT EXISTS precos_energeticos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT NOT NULL UNIQUE,
    preco_usd REAL NOT NULL,
    unidade TEXT DEFAULT 'USD',
    fonte TEXT,
    criado_em TEXT DEFAULT (datetime('now'))
);

-- Tabela Selic histórico
CREATE TABLE IF NOT EXISTS selic_historico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    valor REAL NOT NULL,
    fonte TEXT,
    criado_em TEXT DEFAULT (datetime('now'))
);

-- Tabela empresas RJ
CREATE TABLE IF NOT EXISTS empresas_rj (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    codigo_b3 TEXT UNIQUE,
    setor TEXT,    preco_atual REAL,
    preco_selix REAL,
    potencial_percentual REAL,
    status TEXT DEFAULT 'ativo',
    criado_em TEXT DEFAULT (datetime('now'))
);

-- Tabela sentimento indicadores
CREATE TABLE IF NOT EXISTS sentimento_indicadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentimento TEXT NOT NULL,
    score REAL NOT NULL,
    fontes TEXT,
    criado_em TEXT DEFAULT (datetime('now'))
);

-- Tabela métricas históricas
CREATE TABLE IF NOT EXISTS metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    cpu_percent REAL,
    memory_percent REAL,
    api_healthy INTEGER,
    worker_running INTEGER,
    coverage_percent REAL
);

-- Tabela API keys
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,
    plan TEXT DEFAULT 'free',
    rate_limit_per_minute INTEGER DEFAULT 60,
    expires_at TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    last_used_at TEXT,
    total_requests INTEGER DEFAULT 0
);
SQL

echo "   ✅ Tabelas principais criadas"

# 2. Inserir dados iniciais
echo ""
echo "📦 Passo 2/5: Inserindo dados iniciais..."
sqlite3 "$DB_PATH" << 'SQL'
-- Commodities
INSERT OR IGNORE INTO commodities (nome, preco_usd, unidade, fonte) VALUES    ('Brent', 95.19, 'USD', 'yfinance'),
    ('WTI', 91.45, 'USD', 'yfinance'),
    ('Natural Gas', 2.85, 'USD', 'yfinance'),
    ('Gold', 2345.60, 'USD', 'yfinance'),
    ('Silver', 28.45, 'USD', 'yfinance');

-- Preços energéticos
INSERT OR IGNORE INTO precos_energeticos (produto, preco_usd, unidade, fonte) VALUES
    ('Gasolina', 3.25, 'BRL/l', 'anp'),
    ('Diesel', 2.98, 'BRL/l', 'anp'),
    ('Etanol', 2.85, 'BRL/l', 'anp'),
    ('GNV', 1.95, 'BRL/m3', 'anp');

-- Selic
INSERT OR IGNORE INTO selic_historico (tipo, valor, fonte) VALUES
    ('meta', 10.50, 'bacen'),
    ('efetiva', 14.25, 'bacen');

-- Empresas RJ
INSERT OR IGNORE INTO empresas_rj (nome, codigo_b3, setor, preco_atual, preco_selix, potencial_percentual) VALUES
    ('Petrobras', 'PETR4', 'Energia', 38.50, 42.00, 9.1),
    ('Vale', 'VALE3', 'Mineração', 62.30, 68.50, 10.0),
    ('Ambev', 'ABEV3', 'Bebidas', 14.20, 15.80, 11.3);

-- Sentimento
INSERT OR IGNORE INTO sentimento_indicadores (sentimento, score, fontes) VALUES
    ('neutro', 0.0, 'twitter,news');
SQL

echo "   ✅ Dados iniciais inseridos"

# 3. Criar tabelas geoenergéticas
echo ""
echo "📦 Passo 3/5: Criando tabelas geoenergéticas..."
sqlite3 "$DB_PATH" << 'SQL'
CREATE TABLE IF NOT EXISTS risco_geoenergetico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pais TEXT NOT NULL UNIQUE,
    score REAL NOT NULL,
    rating TEXT,
    fatores TEXT,
    atualizado_em TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS precos_energia_global (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regiao TEXT NOT NULL,
    tipo_energia TEXT NOT NULL,
    preco REAL NOT NULL,
    unidade TEXT,    atualizado_em TEXT DEFAULT (datetime('now'))
);
SQL

echo "   ✅ Tabelas geoenergéticas criadas"

# 4. Calcular índice de confiança (AGORA que commodities existe)
echo ""
echo "📦 Passo 4/5: Calculando índice de confiança..."
cd /root/selix
if python3 confidence/calculator.py 2>&1; then
    echo "   ✅ Índice de confiança calculado"
else
    echo "   ⚠️  Falha ao calcular confiança (continuando...)"
fi

# 5. Verificação final
echo ""
echo "📦 Passo 5/5: Verificação final..."
sqlite3 "$DB_PATH" << 'SQL'
.mode column
.headers on
SELECT 'commodities' as tabela, COUNT(*) as registros FROM commodities
UNION ALL
SELECT 'precos_energeticos', COUNT(*) FROM precos_energeticos
UNION ALL
SELECT 'selic_historico', COUNT(*) FROM selic_historico
UNION ALL
SELECT 'empresas_rj', COUNT(*) FROM empresas_rj;
SQL

echo ""
echo "================================================"
echo "✅ Migração concluída com sucesso!"
echo "================================================"
