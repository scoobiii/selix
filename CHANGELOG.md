# Changelog do SELIX

## [4.0.0] - 2026-06-01

### Added
- API v4.0 com 12 endpoints documentados
- Worker resiliente com fallbacks inteligentes
- Módulo de risco geoenergético global
- Índice de confiança calculado (não inventado)
- Separação entre fatos (observações) e cenários (projeções)
- Testes automatizados (pytest + k6)
- Rate limiting via NGINX
- Benchmarks de carga e estresse

### Changed
- Migração para arquitetura com proveniência (fontes, observações, cenários)
- SQLite otimizado com WAL mode
- Bot do Bluesky agora publica threads segmentadas

### Fixed
- Correção de latência (WAL mode)
- Correção de warnings do pytest
- Cobertura de código aumentada para 41%

## [3.5.0] - 2026-05-31

### Added
- Primeira versão funcional do worker
- API básica com endpoints de energia
- Bot do Bluesky com posts manuais

## [3.0.0] - 2026-05-30

### Added
- Prova formal com Z3 e Lean4
- Modelo matemático da Selic ideal (9,25%)
