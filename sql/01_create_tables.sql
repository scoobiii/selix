-- ============================================================
-- SELIX - Tabelas Profissionais (Provenance)
-- Versão: v4.0
-- Data: 2026-06-01
-- ============================================================

-- Tabela de fontes
CREATE TABLE IF NOT EXISTS fontes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    tipo TEXT CHECK(tipo IN ('api', 'scenario', 'manual', 'llm', 'inference')),
    confianca REAL DEFAULT 0.5,
    url TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dados observados (reais)
CREATE TABLE IF NOT EXISTS observacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicador TEXT NOT NULL,
    valor REAL NOT NULL,
    unidade TEXT,
    fonte_id INTEGER REFERENCES fontes(id),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    synthetic BOOLEAN DEFAULT 0
);

-- Cenários (projeções)
CREATE TABLE IF NOT EXISTS cenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    modelo TEXT,
    confianca REAL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Projeções por cenário
CREATE TABLE IF NOT EXISTS projecoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cenario_id INTEGER REFERENCES cenarios(id),
    indicador TEXT NOT NULL,
    valor REAL NOT NULL,
    unidade TEXT,
    confianca REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Fatores de risco
CREATE TABLE IF NOT EXISTS fatores_risco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    peso REAL DEFAULT 1.0,
    valor_atual REAL,
    tendencia TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice de confiança histórico
CREATE TABLE IF NOT EXISTS indice_confianca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valor REAL NOT NULL,
    fatores TEXT,  -- JSON com fatores usados
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Posts sociais com metadata
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conteudo TEXT NOT NULL,
    tipo TEXT CHECK(tipo IN ('fato', 'cenario', 'alerta', 'opiniao', 'confianca')),
    fonte_id INTEGER REFERENCES fontes(id),
    synthetic BOOLEAN DEFAULT 0,
    publicado_em TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
