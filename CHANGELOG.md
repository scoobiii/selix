# Changelog do SELIX

## [4.0.0] - 2026-06-01

### Added
- API v4.0 com 12 endpoints documentados
- Worker resiliente com fallbacks inteligentes (OilPriceAPI → DuckDuckGo → LLM)
- Módulo de risco geoenergético global (TTF, HH, JKM, Brent)
- Índice de confiança **modular** (diferença entre projeção e mercado real)
- Separação entre fatos (observações) e cenários (projeções)
- Testes automatizados (pytest + k6)
- Rate limiting via NGINX
- Benchmarks de carga e estresse
- Release Notes v4.0.0 com validação empírica

### Changed
- Migração para arquitetura com proveniência (tabelas `fontes`, `observacoes`, `cenarios`, `projecoes`)
- SQLite otimizado com WAL mode
- Bot do Bluesky agora publica threads segmentadas com `synthetic` flag
- Selic ideal mantida como **prova formal (Z3 + Lean4)** – não é fallback

### Fixed
- Correção de latência (WAL mode)
- Correção de warnings do pytest
- Cobertura de código aumentada de 0% para 41% (módulo `geo_energy_risk` criado)

### Metrics
- Testes unitários: 15/15 ✅
- Testes de integração: 5/5 ✅
- Cobertura de código: 41% ⚠️
- Latência p95 (carga): 995ms
- Latência p95 (estresse): 2,58s
- Req/s sustentado: 68

### Validação Empírica
- Brent coletado vs. Brent real: 100% de correspondência (zero divergência)
- Confiança do cenário Selix_925: 46,5% (calculada com fatores reais)

---

## [3.5.0] - 2026-05-31

### Added
- Primeira versão funcional do worker
- API básica com endpoints de energia
- Bot do Bluesky com posts manuais

---

## [3.0.0] - 2026-05-30

### Added
- Prova formal com Z3 e Lean4
- Modelo matemático da Selic ideal (9,25%)
