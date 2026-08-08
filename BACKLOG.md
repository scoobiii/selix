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
