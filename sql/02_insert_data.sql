-- ============================================================
-- SELIX - Inserção de fontes e cenários
-- ============================================================

-- Inserir fontes
INSERT OR IGNORE INTO fontes (nome, tipo, confianca, url) VALUES
    ('OilPriceAPI', 'api', 0.95, 'https://oilpriceapi.com'),
    ('BCB_Selic', 'api', 0.98, 'https://api.bcb.gov.br'),
    ('B3_Fundamentus', 'api', 0.90, 'https://fundamentus.com.br'),
    ('AwesomeAPI', 'api', 0.85, 'https://awesomeapi.com.br'),
    ('YFinance', 'api', 0.92, 'https://finance.yahoo.com'),
    ('Reuters_RSS', 'api', 0.75, 'https://reuters.com'),
    ('Cenario_Selix_925', 'scenario', 0.75, NULL),
    ('LLM_Qwen_Estimate', 'llm', 0.60, NULL),
    ('Inference_Confidence', 'inference', 0.85, NULL);

-- Criar cenário Selix_925
INSERT OR IGNORE INTO cenarios (nome, descricao, modelo, confianca) VALUES
    ('Selix_925', 'Cenário com Selic reduzida para 9,25%', 'selix_v4.0', 0.75);

-- Inserir projeções do cenário
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

-- Selic 1D projetada (fórmula científica)
INSERT OR IGNORE INTO projecoes (cenario_id, indicador, valor, unidade, confianca)
SELECT 
    (SELECT id FROM cenarios WHERE nome='Selix_925'),
    'selic_1d', 
    ROUND((POWER(1.0925, 1.0/252) - 1) * 100, 4),
    '%', 
    0.85
WHERE NOT EXISTS (SELECT 1 FROM projecoes WHERE indicador='selic_1d');

-- Inserir fatores de risco
INSERT OR IGNORE INTO fatores_risco (nome, peso, valor_atual) VALUES
    ('vol_brent', 0.25, 0.0),
    ('vol_combustiveis', 0.20, 0.0),
    ('risco_geo', 0.20, 0.0),
    ('sentimento_global', 0.25, 0.0),
    ('mix_energetico', 0.10, 0.0);

