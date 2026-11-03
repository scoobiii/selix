# 📋 BACKLOG — SELIX v7.2


## ✅ Concluído em 11/08/2026

| Item | Status |
|------|--------|
| Publicador de Snapshot no Bluesky (CI) | ✅ |
| Fonte Única de Verdade no bot (`SELIC_IDEAL` + `DIFERENCIAL`) | ✅ |
| Workflow GitHub Actions (`bluesky_ci.yml`) | ✅ |
| Política anti-fallback (falha visível) | ✅ |

## ⏳ Próximo (Agente de Respostas)

| Item | Prioridade | Status |
|------|------------|--------|
| Monitoramento de menções/respostas | Alta | ⏳ Não iniciado |
| Filtro de perfis alinhados (lista branca) | Alta | ⏳ Não iniciado |
| Respostas automáticas com números oficiais | Alta | ⏳ Não iniciado |
| Workflow `agente_respostas.yml` | Alta | ⏳ Não iniciado |

## ✅ Sprint GOS8 — Concluído (08/08/2026)

| Item | Status |
|------|--------|
| SQLite WAL otimizado | ✅ |
| metrics_agent 100% | ✅ |
| roic_cvm com fallback | ✅ |
| Admin API 100% | ✅ |
| API pública 100% | ✅ |
| CI/CD GCloud Run | ✅ |
| Testes 69/69 | ✅ |
| Cobertura 83% | ✅ |

## ⏳ Próximos (v8.0)

| Item | Prioridade | Esforço |
|------|------------|---------|
| Deploy no GCloud Run | Alta | 2h |
| Dados dinâmicos (API Focus) | Alta | 4h |
| Dashboard web (Streamlit) | Média | 4h |
| Redis cache | Média | 4h |
| PostgreSQL (Supabase) | Média | 4h |

## 🏆 Concluído (v7.2)

- Modelo regime-dependente com multiplicador de credibilidade
- Endpoints de crédito PF/PJ (/v1/credito/*)
- Bloqueio energético τ (E32/B15)
- Credibilidade calculada (0.35)
- Selic ideal = 8.25%
- 69/69 testes passando

## 🧹 Dívida Técnica (identificada)

| Item | Descrição | Prioridade |
|------|-----------|------------|
| `importlib.reload` nos testes | Testes de schema contract usam `importlib.reload()` para ler `SELIX_DB_PATH`. Causa raiz: módulo importado antes do monkeypatch. Investigar e eliminar workaround. | Baixa |
| Documentação do Redis | README não menciona Redis como dependência opcional. | Média |

## 🔒 Selo de Auditoria — GATEADO (não lançar antes disso)

| Pré-requisito | Status | Critério de conclusão |
|---------------|--------|----------------------|
| **Validação de Mercado (Big Five)** | ❌ Não iniciado | ≥ 2 das 5 maiores asset managers usam o Selix como referência |
| **Peer review acadêmico** | ❌ Não iniciado | Publicação em periódico com revisão por pares (ex: Brazilian Journal of Economics) |
| **Track record verificável** | ❌ Não iniciado | Previsão com timestamp pré-Copom vs. resultado real (pelo menos 6 meses de histórico) |

⚠️ **Não comercializar/anunciar o Selo** até os três itens acima estarem ✅.

**Validação de Mercado (Big Five) = Asset Managers**  
- Itaú Asset
- Bradesco Asset
- XP Asset
- JGP / SPX
- Verde Asset

**Critério:** ≥ 2 das 5 adotarem o Selix como referência interna para precificação de ativos (não necessariamente pagando, mas usando como input).

**Implicação prática:**
- **Agora (v7.2/v8.0):** Vender acesso à API e relatórios. **NÃO** vender "Selo de Auditoria".
- **Futuro (v9.0, após validação):** Lançar o "Selo de Auditoria" com lastro de mercado (Big Five).

**Prazo estimado:** Q1 2027 (após validação das asset managers).

## 🔒 Selo GOS3 (Processo) — GATEADO (não declarar antes disso)

Diferente do Selo de Auditoria SELIX (validação de mercado externa), o Selo GOS3
certifica o **protocolo de engenharia**, não o modelo econômico. É auto-verificável
pelos próprios artefatos do repositório — não depende de validação de terceiros.

| Critério | Status | Critério de conclusão |
|----------|--------|----------------------|
| **Anti-truncation policy** | ✅ Provável | Nenhum commit com `...` ou código cortado nos últimos 30 dias |
| **Handoff/Decisions/Gotchas** | ⚠️ Parcial | `docs/handoff.md`, `docs/decisions.md`, `docs/gotchas.md` atualizados a cada sessão (≥ 5 sessões consecutivas) |
| **3 fases pré-código** | ❌ Não iniciado | Log de decisões por feature (Discovery → Refinement → Architecture) documentado em `docs/decisions.md` |
| **CI automatizado** | ❌ Não iniciado | GitHub Actions rodando `pytest` a cada push na `main` |
| **Reprodutibilidade cross-ambiente** | ⚠️ Parcial | CI passa em Ubuntu + Termux + proot-distro (≥ 2 ambientes distintos) |
| **Zero regressão sustentada** | ❌ Não iniciado | Nenhum teste quebrado por > 24h nas últimas 4 semanas consecutivas |

⚠️ **Não declarar "GOS3-compliant"** até os 6 critérios acima estarem ✅.

**GOS3 = Protocolo de Engenharia**
- Mede **como** o código é construído, não **o que** o código faz.
- Auto-verificável pelo repositório (não depende de validação externa).
- Pode ser alcançado **independentemente** do Selo SELIX (não espera validação de mercado).

**Comparação com Selo SELIX:**

| Dimensão | Selo GOS3 | Selo SELIX |
|----------|-----------|------------|
| O que mede | Processo de engenharia | Validação econômica |
| Quem valida | Auto-verificável (repositório) | Mercado (Big Five asset managers) |
| Gates | CI, handoff, reprodutibilidade | Asset managers, peer review, track record |
| Depende de | Ninguém | Validação externa |

**Prazo estimado:** sem compromisso de data — item de maior alavancagem é configurar CI (item 4), do qual os demais critérios (zero regressão, reprodutibilidade) dependem para virar evidência contínua em vez de foto manual.


## 🔒 Selo GOS3 — GATEADO (Dia 1/7)

| Critério | Status | Critério de conclusão |
|----------|--------|----------------------|
| CI automatizado | ✅ | GitHub Actions rodando pytest a cada push |
| Zero regressão | ⏳ | 7 dias consecutivos sem quebra |
| Reprodutibilidade | ⏳ | CI passa em Ubuntu + Termux |
| Handoff/Decisions | ⏳ | docs/handoff.md atualizado |

⚠️ **Não declarar "GOS3-compliant"** até os 4 critérios acima estarem ✅.

**Prazo estimado:** 16/08/2026

## SELIX Recovery — estado em 2026-11

Este bloco registra o estado da linha de desenvolvimento Recovery.
Não substitui nem reclassifica as entregas históricas das versões anteriores.

### Implementado na branch `feat/selix-recovery-model`

| Entrega | Estado |
|---|---|
| Extração de dados DFP/ITR da CVM por empresa e período | Implementada |
| Tratamento de descrições alternativas de despesas financeiras | Implementado |
| Alerta para resultado financeiro sem despesa detalhada | Implementado |
| Cálculo de cobertura de juros com dados disponíveis | Implementado |
| Sensibilidade da dívida | Implementada |
| Reconciliação PL inicial + lucro líquido versus PL final | Implementada |
| Alerta de variação do PL não explicada pelo lucro | Implementado |
| Testes específicos de Recovery | Resultados aprovados reportados durante o desenvolvimento |

### Próximas entregas

| Item | Prioridade | Critério de aceite |
|---|---|---|
| Persistência única para histórico multiempresa | Alta | Dados versionados, consultáveis e reproduzíveis |
| Modelo de proveniência por métrica | Alta | Fonte, conta CVM, período, perímetro, unidade e método registrados |
| Reconciliação de dívida, caixa e arrendamentos | Alta | Divergências explicitadas e testadas |
| Normalização de demonstrações | Alta | DRE, BP e DFC com escalas e períodos consistentes |
| API/SDK para consumidores humanos e agentes | Média | Contratos documentados e testes de integração |
| Dashboard multiempresa | Média | Séries comparáveis com origem e limitações visíveis |
| Exportação de relatórios auditáveis | Média | Resultados reproduzíveis e rastreáveis |

### Arquitetura proposta — ainda não declarar como implementada

CVM/DFP/ITR → ingestão e extração → normalização contábil →
validação e proveniência → persistência Recovery → API/SDK →
dashboard humano, agentes e relatórios.

A persistência deve ser única, servindo tanto consumidores humanos quanto
agentes. SQLite pode atender à fase local; PostgreSQL pode ser avaliado
para implantação multiusuário. Essa arquitetura é uma proposta de evolução,
não uma declaração de que esses serviços já estão disponíveis.

### Critério de promoção para release

- Testes de unidade e integração aprovados.
- Casos de referência contábil revisados.
- Proveniência e limitações documentadas.
- Compatibilidade e contratos públicos definidos.
- Documentação e changelog revisados.
- Nenhuma alteração acidental nos snapshots oficiais.
