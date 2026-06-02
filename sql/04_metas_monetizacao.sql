-- 04_metas_monetizacao.sql
-- Popula a tabela metas com alvos iniciais de monetização do SELIX
-- Execute: sqlite3 /root/selix/selix.db < sql/04_metas_monetizacao.sql

INSERT OR IGNORE INTO metas (segmento, indicador, meta_valor, unidade, data_inicio, data_fim)
VALUES
  -- MRR e clientes gerais
  ('geral',    'mrr',             5000.0, 'BRL',     date('now'), date('now', '+90 days')),
  ('geral',    'clientes_pagos',    10.0, 'unidades', date('now'), date('now', '+90 days')),

  -- Conversão via Bluesky
  ('bluesky',  'clientes_pagos',    3.0,  'unidades', date('now'), date('now', '+30 days')),
  ('bluesky',  'mrr',             500.0,  'BRL',      date('now'), date('now', '+30 days')),

  -- Conteúdo (semanal)
  ('conteudo', 'posts_cta',         5.0,  'posts',    date('now'), date('now', '+7 days')),
  ('conteudo', 'cliques',          50.0,  'cliques',  date('now'), date('now', '+7 days')),
  ('conteudo', 'taxa_conversao',    1.0,  '%',        date('now'), date('now', '+30 days'));

-- Confirma
SELECT segmento, indicador, meta_valor, unidade FROM metas ORDER BY segmento, indicador;
