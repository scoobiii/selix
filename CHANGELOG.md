# 📝 CHANGELOG — SELIX

## [v7.2] — 2026-08-08

### Adicionado
- Modelo regime-dependente com multiplicador de credibilidade
- Endpoints de crédito PF/PJ (`/v1/credito/*`)
- Fator de blindagem energética τ (E32/B15)
- Credibilidade calculada (0.35) via histórico 2020-2025
- Fonte única de verdade (`config.py` com SELIC_IDEAL = 8.25%)
- SQLite WAL mode otimizado
- CI/CD para GCloud Run (deploy.yml)

### Corrigido
- Admin API: 6/6 testes passando
- metrics_agent: 20/20 testes passando
- roic_cvm: fallback sem pandas
- test_alertas_geral: dados de teste no banco
- Testes de API com headers padronizados via conftest.py
- Duplicatas de endpoints de crédito removidas

### Testes
- 69/69 testes passando (100%)
- Cobertura geral: 83%
- Cobertura core.py: 100%

### Documentação
- README atualizado para v7.2
- LIMITACOES.md atualizado
- BACKLOG.md criado

---

## [v7.1] — 2026-08-07

### Adicionado
- Primeira versão do modelo regime-dependente
- Endpoint `/v1/credito/pj`

### Corrigido
- Credibilidade hardcoded → calculada

---

## [v4.0.0] — 2026-06-01

### Added
- API v4.0 com 12 endpoints documentados
- Worker resiliente com fallbacks inteligentes
- Módulo de risco geoenergético global
- Índice de confiança calculado
- Separação entre fatos e cenários
- Testes automatizados (pytest + k6)
- Rate limiting via NGINX

### Changed
- Migração para arquitetura com proveniência
- SQLite otimizado com WAL mode
- Bot do Bluesky com threads segmentadas

### Fixed
- Correção de latência (WAL mode)
- Correção de warnings do pytest
- Cobertura de código aumentada para 41%

## [3.5.0] — 2026-05-31

### Added
- Primeira versão funcional do worker
- API básica com endpoints de energia
- Bot do Bluesky com posts manuais
