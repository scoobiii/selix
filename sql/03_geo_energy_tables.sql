-- ============================================================
-- SELIX - Tabelas de Matriz Energética e Risco Geoenergético
-- Versão: v4.0
-- ============================================================

-- Tabela de fontes energéticas globais
CREATE TABLE IF NOT EXISTS matriz_energetica (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pais TEXT NOT NULL,
    fonte TEXT CHECK(fonte IN ('petroleo', 'gas_natural', 'carvao', 'nuclear', 'hidro', 'eolica', 'solar', 'biomassa', 'etanol', 'biodiesel', 'biogas', 'geotermica', 'maremotriz')),
    capacidade_gw REAL,
    producao_mwh REAL,
    emissao_co2_ton REAL,
    peso_matriz REAL DEFAULT 0,
    fonte_dados TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de preços energéticos globais
CREATE TABLE IF NOT EXISTS precos_energia_global (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regiao TEXT,
    produto TEXT CHECK(produto IN ('TTF', 'HH', 'JKM', 'Brent', 'WTI', 'Gasolina', 'Diesel', 'Etanol', 'Biodiesel', 'GN', 'GLP')),
    preco_usd REAL,
    unidade TEXT,
    tendencia TEXT,
    fonte TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de risco geoenergético por país
CREATE TABLE IF NOT EXISTS risco_geoenergetico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pais TEXT UNIQUE,
    score REAL DEFAULT 0.5,
    rating TEXT CHECK(rating IN ('AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'D')),
    fatores TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de investment grade (com agências)
CREATE TABLE IF NOT EXISTS investment_grade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pais TEXT UNIQUE,
    rating TEXT,
    score REAL,
    perspectiva TEXT,
    agencia TEXT CHECK(agencia IN ("S&P", "Moody''s", "Fitch", "Selix")),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir matriz energética do Brasil
INSERT OR IGNORE INTO matriz_energetica (pais, fonte, peso_matriz, emissao_co2_ton, fonte_dados) VALUES
    ('Brasil', 'hidro', 0.65, 0, 'ANEEL'),
    ('Brasil', 'eolica', 0.12, 0, 'ONS'),
    ('Brasil', 'solar', 0.08, 0, 'ABSOLAR'),
    ('Brasil', 'biomassa', 0.08, 0, 'UNICA'),
    ('Brasil', 'gas_natural', 0.05, 0.2, 'EPE'),
    ('Brasil', 'nuclear', 0.02, 0, 'Eletronuclear');
