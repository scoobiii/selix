# 📋 BACKLOG — SELIX v7.2

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
