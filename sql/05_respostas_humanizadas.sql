-- 05_respostas_humanizadas.sql
-- Respostas humanizadas por segmento, com CC a stakeholders
-- Formato: cada resposta é uma lista de partes (thread se > 1 parte)
-- Execute: sqlite3 /root/selix/selix.db < sql/05_respostas_humanizadas.sql

-- Adiciona coluna thread_json se não existir
ALTER TABLE respostas_banco ADD COLUMN thread_json TEXT;
ALTER TABLE respostas_banco ADD COLUMN cc_handles TEXT; -- handles separados por vírgula

-- Remove respostas antigas para recriar humanizadas
DELETE FROM respostas_banco;

-- ── TRABALHADORES ────────────────────────────────────────────────────────────────

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('trabalhadores', 'plr',
 '👷 Tá sem PLR? A Selic alta (14,5%) é um dos motivos. Com 9,25% — provado pelo SELIX — sobrariam R$270bi/ano pra economia real. Exija #TrampoForte! 🧵',
 '@cut.org.br.bsky.social,@forcasindical.bsky.social',
 '[
   "👷 Tá sem PLR? A Selic alta (14,5%) é um dos motivos. Com 9,25% — provado pelo SELIX — sobrariam R$270bi/ano pra economia real. Exija #TrampoForte! 🧵 (1/3)",
   "📊 O SELIX usa 5 teoremas formais (Z3 + Lean4) pra provar que a taxa justa é 9,25%. Não é opinião — é matemática verificada. (2/3)",
   "🔗 Veja os dados, a API e o código aberto: github.com/scoobiii/selix\nCC: @cut.org.br.bsky.social @forcasindical.bsky.social #Selix #PLR (3/3)"
 ]');

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('trabalhadores', 'salario',
 '💰 Salário não estica? Inflação + Selic alta corroem seu poder de compra todo mês. O SELIX prova: com 9,25% isso muda. #Selix 🧵',
 '@cut.org.br.bsky.social,@mte.gov.br.bsky.social',
 '[
   "💰 Salário não estica? Inflação + Selic alta corroem seu poder de compra todo mês. O SELIX prova: com 9,25% isso muda. 🧵 (1/3)",
   "📉 Cada 1% a menos na Selic = R$27bi devolvidos à economia real. Com -5,25pp (de 14,5% pra 9,25%) = R$270bi/ano. Pra você, não pro rentismo. (2/3)",
   "🔗 github.com/scoobiii/selix\nCC: @cut.org.br.bsky.social @mte.gov.br.bsky.social #TrampoForte #Selix (3/3)"
 ]');

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('trabalhadores', 'desemprego',
 '😔 Desemprego alto tem endereço: crédito caro, Selic nas alturas. O SELIX calcula a taxa que libera geração de empregos. #TrampoForte 🧵',
 '@cut.org.br.bsky.social,@dieese.org.br.bsky.social',
 '[
   "😔 Desemprego alto tem endereço: crédito caro, Selic nas alturas. O SELIX calcula a taxa que libera geração de empregos. 🧵 (1/3)",
   "🏭 Com Selic a 9,25%, empresas conseguem crédito pra contratar. GPA e Raízen já têm upside projetado de +68% e +76% nesse cenário. (2/3)",
   "🔗 Dados abertos: github.com/scoobiii/selix\nCC: @cut.org.br.bsky.social @dieese.org.br.bsky.social #Selix #TrampoForte (3/3)"
 ]');

-- ── INVESTIDORES ─────────────────────────────────────────────────────────────────

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('investidores', 'valuation',
 '📈 Valuation travado pela Selic? Cenário Selix_925 projeta GPA +68% e Raízen +76%. API aberta pra integrar no seu modelo. 🧵',
 '@b3.bsky.social,@anbima.bsky.social',
 '[
   "📈 Valuation travado pela Selic? Cenário Selix_925 projeta GPA (PCAR3) +68% e Raízen (RAIZ4) +76% com Selic a 9,25%. 🧵 (1/3)",
   "🏦 Macro do cenário: PIB per capita US$130k (+118%), B3 Market Cap US$10tri, Investment Grade A-. Tudo modelado com dados reais do BCB e B3. (2/3)",
   "🔗 API: curl https://api.selix.com/v1/empresas/rj\nCódigo: github.com/scoobiii/selix\nCC: @b3.bsky.social @anbima.bsky.social #Selix (3/3)"
 ]');

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('investidores', 'b3',
 '🏦 B3 pode valer US$10 trilhões com Selic 9,25% (Selix_925). Dados reais + projeções na API. Veja o modelo. 🧵',
 '@b3.bsky.social,@anbima.bsky.social',
 '[
   "🏦 B3 vale hoje ~US$1,6tri. Com Selic 9,25% (cenário Selix_925), a projeção é US$10tri — 6x o valor atual. Como chegamos nisso? 🧵 (1/3)",
   "📊 Queda de custo de capital → expansão de múltiplos → reavaliação de toda a bolsa. O SELIX usa 5 teoremas formais pra embasar cada número. (2/3)",
   "🔗 Explore: github.com/scoobiii/selix | API: /v1/empresas/rj\nCC: @b3.bsky.social @anbima.bsky.social #Selix #Investimentos (3/3)"
 ]');

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('investidores', 'juros',
 '💹 Juro real de 8%+ é custo de capital insustentável. O SELIX prova com Z3+Lean4 que 9,25% é o equilíbrio. Thread com os dados: 🧵',
 '@b3.bsky.social,@anbima.bsky.social',
 '[
   "💹 Juro real brasileiro ~8%+ é um dos maiores do mundo. Isso mata valuation, emprego e consumo. Mas qual seria o justo? 🧵 (1/3)",
   "🔬 O SELIX usa 5 teoremas provados (Z3 + Lean 4) e dados reais (BCB, Brent, B3) pra calcular: Selic ideal = 9,25%. Não é chute. (2/3)",
   "🔗 Código aberto: github.com/scoobiii/selix\nCC: @b3.bsky.social @anbima.bsky.social #Selix #JuroReal (3/3)"
 ]');

-- ── AMBIENTALISTAS ───────────────────────────────────────────────────────────────

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('ambientalistas', 'etanol',
 '🌱 Com Brent a US$97, o mix ideal é E35/B20. O SELIX calcula isso em tempo real e evita emissões desnecessárias. 🧵',
 '@greenpeace.bsky.social,@sosflorestas.bsky.social',
 '[
   "🌱 Sabia que o mix etanol/biodiesel ideal muda com o preço do petróleo? Com Brent a US$97, o SELIX indica E35/B20. 🧵 (1/3)",
   "🌎 Com esse mix otimizado, o Brasil pode evitar 200 milhões de toneladas de CO₂/ano — sem abrir mão da competitividade energética. (2/3)",
   "🔗 API em tempo real: /v1/energia/mistura\ngithub.com/scoobiii/selix\nCC: @greenpeace.bsky.social @sosflorestas.bsky.social #Selix #Bioeconomia (3/3)"
 ]');

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('ambientalistas', 'emissoes',
 '🌎 Menos Selic = mais crédito verde = mais solar e biogás. O SELIX conecta política monetária e transição energética. 🧵',
 '@greenpeace.bsky.social,@ipam.org.br.bsky.social',
 '[
   "🌎 A Selic alta suga crédito que poderia financiar solar, eólica e biogás. Com 9,25%, o custo do capital verde cai pela metade. 🧵 (1/3)",
   "☀️ Matriz atual: Hidro 65%, Eólica 12%, Solar 8%, Biomassa 8%. Com crédito barato, solar e biogás podem dobrar em 5 anos. (2/3)",
   "🔗 github.com/scoobiii/selix | API: /v1/energia/mistura\nCC: @greenpeace.bsky.social @ipam.org.br.bsky.social #Selix #TransicaoEnergetica (3/3)"
 ]');

-- ── GOVERNO ──────────────────────────────────────────────────────────────────────

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('governo', 'divida',
 '🏛️ Dívida pública custando R$650bi/ano. Com Selic 9,25% (SELIX), cai pra R$380bi. R$270bi livres pra investimento. 🧵',
 '@fazenda.gov.br.bsky.social,@bcb.gov.br.bsky.social',
 '[
   "🏛️ O Brasil gasta R$650bi/ano só com juros da dívida pública — mais do que saúde e educação juntos. Existe saída? 🧵 (1/3)",
   "📉 O SELIX prova com 5 teoremas formais que a Selic ideal é 9,25%. Nesse cenário: custo da dívida = R$380bi. Economia: R$270bi/ano. (2/3)",
   "🔗 Modelo aberto: github.com/scoobiii/selix\nCC: @fazenda.gov.br.bsky.social @bcb.gov.br.bsky.social #Selix #PoliticaFiscal (3/3)"
 ]');

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('governo', 'rating',
 '📊 Score geoenergético BR: 0,266 (4º mundo). Rating Selix: AA. Investment grade está ao alcance com política monetária correta. 🧵',
 '@fazenda.gov.br.bsky.social,@bcb.gov.br.bsky.social',
 '[
   "📊 O Brasil tem o 4º melhor score geoenergético do mundo (0,266 no modelo SELIX). Mas o rating soberano ainda é BB. Por quê? 🧵 (1/3)",
   "🏦 Porque a Selic alta sinaliza risco fiscal elevado. Com 9,25%, o modelo projeta upgrade para A- em 24 meses — investment grade. (2/3)",
   "🔗 github.com/scoobiii/selix | API: /v1/sentimento\nCC: @fazenda.gov.br.bsky.social @bcb.gov.br.bsky.social #Selix #InvestmentGrade (3/3)"
  ]');

-- ── GERAL ────────────────────────────────────────────────────────────────────────

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('geral', 'selic',
 '📉 Selic ideal provada com Z3+Lean4: 9,25% (atual: 14,50%). Economia de R$270bi/ano. 5 teoremas, código aberto. 🧵',
 '@bcb.gov.br.bsky.social',
 '[
   "📉 Por que a Selic está em 14,50% sendo que a taxa ideal é 9,25%? O SELIX tem a resposta — e ela é matemática. 🧵 (1/3)",
   "🔬 5 teoremas provados formalmente com Z3 (Microsoft) e Lean 4 mostram que qualquer taxa acima de 9,99% é ineficiente e injusta. (2/3)",
   "🔗 Veja, teste, contribua: github.com/scoobiii/selix\nCC: @bcb.gov.br.bsky.social #Selix #PoliticaMonetaria (3/3)"
 ]');

INSERT INTO respostas_banco (segmento, dor_keyword, resposta, cc_handles, thread_json) VALUES
('geral', 'default',
 '🤖 Oi! Sou o bot do SELIX — sistema que prova que a Selic ideal é 9,25% (hoje: 14,50%). Saiba mais: github.com/scoobiii/selix #Selix',
 NULL,
 '[
   "🤖 Oi! Sou o bot do SELIX — sistema econômico experimental que prova, com matemática formal, que a Selic ideal é 9,25%. 🧵 (1/2)",
   "🔗 Código aberto, API REST, dados reais do BCB e mercado: github.com/scoobiii/selix\n#Selix #TrampoForte #InvestmentGrade (2/2)"
 ]');

-- Confirma
SELECT segmento, dor_keyword, length(resposta) AS chars, json_array_length(thread_json) AS partes
FROM respostas_banco ORDER BY segmento, dor_keyword;
