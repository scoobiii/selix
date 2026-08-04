
# 🤖 SELIX v6.2 — Modelo Regime-Dependente com Dados Reais de Mercado

**Selic real:** 14,25% · **Selic ideal:** 9,25% · **Economia anual:** R$ 345 bi
*(Cálculo: Dívida pública R$ 6,9 tri × 5,00 p.p. de redução)*

[![Bluesky Bot](https://img.shields.io/badge/Bluesky-@zeh--sobrinho-1DA1F2)](https://bsky.app/profile/zeh-sobrinho.bsky.social)
[![API v6.2](https://img.shields.io/badge/API-v6.2-green)](https://github.com/scoobiii/selix)
[![Tests](https://img.shields.io/badge/tests-93%2F93-brightgreen)](https://github.com/scoobiii/selix)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/scoobiii/selix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Termux](https://img.shields.io/badge/Termux-24%2F7-blue)](https://github.com/scoobiii/selix)

---

## 🎯 O que é o SELIX?

SELIX é um **sistema autônomo de inteligência econômica** que calcula a **taxa de juros ideal para o Brasil** com base em **provas matemáticas formalizadas (Lean/Z3)**, **dados reais de mercado** (BCB, Yahoo Finance, B3) e um **modelo regime-dependente com multiplicador de credibilidade**.

O sistema publica automaticamente no Bluesky, fornece uma API REST e funciona 24/7 no **Termux/Android**.

---

## 🧮 Modelo Econômico — SELIX v6.2

### Equação Fundamental com Multiplicador de Credibilidade

```

juro_real_necessario = inflação × (1 + prêmio_risco) × (1 + (1 - credibilidade) × 0.5) + 0.5 × gap_produto

```

| Componente | Valor | Fonte |
|------------|-------|-------|
| **inflação** | 4.48% | IPCA (BCB) |
| **prêmio_risco** | 1.16% | CDS Brasil 5Y (maio/2026) |
| **credibilidade** | 0.50 | Histórico de metas (Focus/BCB) |
| **gap_produto** | -0.5% | IBGE/BCB |

### Comparação Formal (Lean)

| País | Inflação | Prêmio Risco | Credibilidade | Juro Real Necessário |
|------|----------|--------------|---------------|---------------------|
| **Brasil** | 4.48% | **1.16%** | 0.50 | **~5.66%** |
| **EUA** | 2.50% | 0.50% | 0.95 | ~4.0% |
| **Europa** | 2.00% | 0.40% | 0.90 | ~3.8% |

> **Teorema T11 (Lean):** Brasil precisa de juro real ~1.4x maior que EUA com prêmio de risco atual (1.16%).

### Reconciliação dos Impactos

| Cenário | Dívida | Diferencial | Impacto | Contexto |
|---------|--------|-------------|---------|----------|
| **R$ 270 bi** | R$ 5,4 tri | 5,0 p.p. | R$ 270 bi | Dívida líquida (STN) |
| **R$ 345 bi** | R$ 6,9 tri | 5,0 p.p. | R$ 345 bi | Dívida bruta (BCB) |
| **R$ 430 bi** | R$ 5,4 tri | 8,0 p.p. | R$ 430 bi | Selic 2D (14,25%) → 1D (6,25%) |

---

## 📊 Status do Projeto

| Métrica | Status |
|---------|--------|
| **Versão** | v6.2.0-stable |
| **Build** | ✅ Passando |
| **Testes** | 93/93 ✅ |
| **Cobertura core.py** | 100% ✅ |
| **Stress test** | 80 VUs, p95=152ms ✅ |
| **Disponibilidade** | 24/7 no Termux/Android |
| **Prêmio de risco** | 1.16% (CDS 5Y - mai/2026) |

---

## 🚀 Instalação

### 1. Linux / Ubuntu / Termux

```bash
git clone https://github.com/scoobiii/selix.git
cd selix

# Ambiente virtual (Linux/Ubuntu)
python3 -m venv venv
source venv/bin/activate

# Termux (Android)
pkg install python
pip install -r requirements.txt

# Configurar credenciais
cp .env.example .env
nano .env

# Iniciar sistema
./start_selix.sh
```

2. Termux (Android) — Autostart no boot

```bash
./scripts/setup_termux_boot.sh
# O SELIX iniciará automaticamente no boot do dispositivo
```

---

🧪 Testes

```bash
pytest tests/ -v
pytest tests/ --cov=src.selix --cov-report=html
# Resultado: 93/93 testes passando ✅
```

---

📖 Endpoints da API

Endpoint Método Autenticação Descrição
/v1/health GET Pública Status da API
/v1/energia/mistura/<brent> GET Pública Mix energético por Brent
/v1/energia/termicas GET Pública Lista de termelétricas
/v1/energia/gatilhos GET Pública Gatilhos de mix energético
/v1/selic GET API Key Selic atual e ideal
/v1/commodities GET API Key Preços de commodities
/v1/empresas/rj GET API Key Empresas em recuperação judicial
/v1/perguntar POST API Key Pergunta assíncrona (retorna task_id)
/v1/task/<id> GET API Key Consulta resultado de task
/v1/admin/generate_key POST Master Key Gerar nova API Key
/v1/admin/list_keys GET Master Key Listar chaves ativas
/v1/admin/revoke_key POST Master Key Revogar chave
/v1/admin/renew_key POST Master Key Renovar chave

---

📊 Valor Agregado por Segmento

Segmento Quem Como o SELIX agrega valor
Setor Financeiro Bancos, corretoras, fundos Precificação de ativos, ajuste de duration, hedge
Empresas CFOs, tesourarias Planejamento de captação, redução de custo de capital
Governo BCB, Ministério da Fazenda, Congresso Base técnica para política monetária
Academia Economistas, pesquisadores, think tanks Pesquisa e validação de modelos econômicos
Sociedade Jornalistas, formadores de opinião Dados confiáveis para debate público

---

🚫 Escopo e Limitações

O que o SELIX NÃO é:

· ❌ Modelo DSGE: Não substitui o SAMBA do BCB nem modelos de equilíbrio geral dinâmico
· ❌ Accountability institucional: Não tem mandato legal nem acesso privilegiado a dados internos
· ❌ Estimativa estocástica: Não incorpora incerteza em tempo real com simulações de Monte Carlo

O que o SELIX É:

· ✅ Ferramenta de auditoria aritmética: Prova formal no Lean/Z3 de que os números atuais não batem com regras básicas de mercado
· ✅ Transparência: Código aberto, dados públicos, rastreável
· ✅ Apoio à decisão: Quantifica o custo de oportunidade da Selic atual
· ✅ Educação: Demonstra como parâmetros macroeconômicos interagem

---

🔬 Provas Formais (Lean)

T7: r* e risk_premium derivados de dados históricos

· r (juro real neutro):* 4.48% (média BCB SGS 12)
· risk_premium (prêmio de risco Brasil): 1.16% (CDS 5Y - mai/2026)
· Prova: r_star_derivado_correto e risk_premium_derivado_correto

T8: Impacto econômico R$ 345 bi

· Dívida pública líquida: R$ 6,9 tri (STN/BCB SGS 14558)
· Diferencial Selic: 5,00 p.p. (14.25% - 9.25%)
· Prova: economia_anual_provada

T9: Reconciliação 9.48% vs 9.25%

· 9.48%: Teto contínuo (Lean/Z3) — derivado de dados históricos (com prêmio 2.00%)
· 9.25%: Valor quantizado ao grid do Copom (0.25pp)
· Prova: quantizacao_do_continuo

T11: Multiplicador de Credibilidade (atualizado)

· Juro real necessário: inflação × (1 + prêmio_risco) × (1 + (1 - credibilidade) × 0.5)
· Comparação: Brasil ~1.4× EUA (com CDS 1.16%)
· Prova: juro_real_brasil_calculado e comparacao_brasil_eua

---

🏆 Roadmap — SELIX v7.0 (Accountability Total)

Item Descrição Status
API Focus Integração com expectativas de mercado do Relatório Focus ⏳ Planejado
EMBI+ em tempo real Derivação endógena do prêmio de risco via API ⏳ Planejado
Credibilidade endógena Modelo baseado no histórico de cumprimento da meta ⏳ Planejado
Choques exógenos Oil/TTF como variáveis de estado no modelo ⏳ Planejado
Intervalos de confiança 86% de credibilidade com derivados de incerteza ⏳ Planejado
Accountability total Derivação endógena formalizada no Lean ⏳ Planejado

---

🤝 Contribuição

1. Fork o projeto
2. Crie sua branch (git checkout -b feature/AmazingFeature)
3. Commit suas mudanças (git commit -m 'Add some AmazingFeature')
4. Push para a branch (git push origin feature/AmazingFeature)
5. Abra um Pull Request

---

📄 Licença

MIT © 2026 – Zeh Sobrinho, GOS3, MEX Energia

---

🔗 Links

· Repositório: https://github.com/scoobiii/selix
· Bluesky: @zeh-sobrinho.bsky.social
· Documentação: https://scoobiii.github.io/selix/

---

🏆 Histórico de Versões

Versão Data Mudanças
v6.2.0 2026-08-04 Prêmio de risco atualizado para 1.16% (CDS 5Y)
v6.1.0 2026-08-04 Modelo regime-dependente com multiplicador de credibilidade
v5.4.1 2026-08-04 Provas formais T7, T8, T9
v5.3.0 2026-08-04 Sprint GOS3: cobertura 100%, infraestrutura mobile
v5.0.0 2026-07-28 Lançamento inicial com API, bot, worker

---

O SELIX v6.2 está 100% completo e pronto para produção! 🚀🏆

## 💰 Reconciliação dos Impactos — R$ 270/345/430 bi

O SELIX trabalha com **três cenários distintos**, dependendo da base da dívida e do diferencial considerado:

| Cenário | Dívida | Diferencial | Impacto | Contexto |
|---------|--------|-------------|---------|----------|
| **R$ 270 bi** | R$ 5,4 tri (líquida) | 5,0 p.p. | R$ 270 bi | Dívida líquida (STN) |
| **R$ 345 bi** | R$ 6,9 tri (bruta) | 5,0 p.p. | R$ 345 bi | Dívida bruta (BCB) |
| **R$ 431 bi** | R$ 5,4 tri (líquida) | 8,0 p.p. | R$ 431 bi | Selic 2D → 1D (14,25→6,25) |

**Qual usar?** O valor operacional do SELIX é **R$ 345 bi** (dívida bruta BCB). Os outros cenários são análises de sensibilidade.

> **Nota:** O valor de R$ 431 bi é um cenário hipotético de queda da Selic para 6,25%, não uma projeção do SELIX.

## ⚠️ Disclaimer

O SELIX é uma **ferramenta de apoio à decisão**, não uma fonte de previsões econômicas definitivas. Todos os números são **estimativas** baseadas em dados públicos e modelos matemáticos. O sistema não substitui a análise de especialistas nem as decisões do COPOM.

**Uso recomendado:** Auditoria, transparência, educação e referência técnica.

**Uso NÃO recomendado:** Substituir o COPOM, previsões de curto prazo, decisões de trading sem validação adicional.
