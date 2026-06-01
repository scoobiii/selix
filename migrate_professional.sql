-- ============================================================
-- SELIX - Migração para arquitetura profissional (provenance)
-- ============================================================

-- 1. Criar tabelas profissionais
CREATE TABLE IF NOT EXISTS fontes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    tipo TEXT CHECK(tipo IN ('api', 'scenario', 'manual', 'llm')),
    confianca REAL DEFAULT 0.5,
    url TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS observacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicador TEXT NOT NULL,
    valor REAL NOT NULL,
    unidade TEXT,
    fonte_id INTEGER REFERENCES fontes(id),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    synthetic BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS cenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    modelo TEXT,
    confianca REAL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projecoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cenario_id INTEGER REFERENCES cenarios(id),
    indicador TEXT NOT NULL,
    valor REAL NOT NULL,
    unidade TEXT,
    confianca REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conteudo TEXT NOT NULL,
    tipo TEXT CHECK(tipo IN ('fato', 'cenario', 'alerta', 'opiniao')),
    fonte_id INTEGER REFERENCES fontes(id),
    synthetic BOOLEAN DEFAULT 0,
    publicado_em TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Inserir fontes
INSERT OR IGNORE INTO fontes (nome, tipo, confianca, url) VALUES
    ('OilPriceAPI', 'api', 0.95, 'https://oilpriceapi.com'),
    ('BCB_Selic', 'api', 0.98, 'https://api.bcb.gov.br'),
    ('B3_Fundamentus', 'api', 0.90, 'https://fundamentus.com.br'),
    ('AwesomeAPI', 'api', 0.85, 'https://awesomeapi.com.br'),
    ('Cenario_Selix_925', 'scenario', 0.75, NULL),
    ('LLM_Qwen_Estimate', 'llm', 0.60, NULL);

-- 3. Migrar observações existentes
INSERT OR IGNORE INTO observacoes (indicador, valor, unidade, fonte_id, synthetic)
SELECT 'brent', preco_usd, 'USD/bbl', f.id, 0
FROM commodities c
JOIN fontes f ON f.nome = 'OilPriceAPI'
WHERE c.fonte = 'OilPriceAPI'
ORDER BY c.criado_em DESC LIMIT 1;

INSERT OR IGNORE INTO observacoes (indicador, valor, unidade, fonte_id, synthetic)
SELECT 'selic', valor, '%', f.id, 0
FROM selic_historico s
JOIN fontes f ON f.nome = 'BCB_Selic'
WHERE s.fonte = 'BCB'
ORDER BY s.criado_em DESC LIMIT 1;

-- 4. Criar cenário Selix_925
INSERT OR IGNORE INTO cenarios (nome, descricao, modelo, confianca) VALUES
    ('Selix_925', 'Cenário com Selic reduzida para 9,25%', 'selix_v3.5', 0.75);

-- 5. Inserir projeções do cenário
INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'selic_aa', 9.25, '%', 0.95
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='selic_aa');

INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'pib_per_capita', 130000, 'USD', 0.70
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='pib_per_capita');

INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'b3_market_cap', 10e12, 'USD', 0.65
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='b3_market_cap');

INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'gpa_upside', 68.0, '%', 0.60
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='gpa_upside');

INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'raizen_upside', 76.4, '%', 0.60
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='raizen_upside');

INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'investment_grade', 1, 'flag', 0.80
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='investment_grade');

INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'economia_anual', 270, 'Bilhões USD', 0.75
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='economia_anual');

-- 6. Selic 1D projetada (fórmula científica)
INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca, timestamp)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'selic_1d', 
    ROUND((POWER(1.0925, 1.0/252) - 1) * 100, 4),
    '%', 
    0.85,
    datetime('now')
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='selic_1d');

-- 7. Relatório final
SELECT '✅ Migração concluída!' as status;
SELECT 'Fontes: ' || COUNT(*) FROM fontes;
SELECT 'Observações: ' || COUNT(*) FROM observacoes;
SELECT 'Cenários: ' || COUNT(*) FROM cenarios;
SELECT 'Projeções: ' || COUNT(*) FROM projecoes;
