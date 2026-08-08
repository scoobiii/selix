# SELIX v8.0 — Camada HTTP Escalável

## Objetivo
Transformar a camada HTTP do SELIX em uma API escalável, resiliente e pronta para produção.

## Status atual (v7.2)

| Requisito | Atendido? | Observação |
|-----------|-----------|------------|
| Queries demoradas | ❌ | Flask síncrono bloqueia o servidor |
| Resultados enormes | ❌ | Sem streaming ou paginação |
| Falhas/erros | ⚠️ | Tratamento básico, sem retry/circuit breaker |
| Limite de payload | ❌ | Padrão Flask 16MB sem compressão |
| Balanceador de carga | ❌ | 1 instância |
| Performance | ⚠️ | ~50 req/s, sem cache |
| Stress test | ❌ | Não testado com k6/vegeta |
| GCloud Run | ⚠️ | Roda, mas sem otimização |

## Itens para v8.0

| # | Item | Descrição | Prioridade | Esforço |
|---|------|-----------|------------|---------|
| 1 | **FastAPI** | Migrar de Flask para FastAPI (async, HTTP/2) | Alta | 8h |
| 2 | **Streaming** | Respostas chunked para dados grandes | Alta | 4h |
| 3 | **Paginação** | `limit` e `offset` em todos os endpoints GET | Alta | 4h |
| 4 | **Redis Cache** | Cache de ROIC, WACC, Selic | Alta | 4h |
| 5 | **PostgreSQL** | Migrar do SQLite para Supabase/Neon | Alta | 4h |
| 6 | **Rate limiting distribuído** | Redis + sliding window | Média | 4h |
| 7 | **Circuit Breaker** | `tenacity` ou `circuitbreaker` para APIs externas | Média | 4h |
| 8 | **NGINX** | Balanceador de carga + SSL | Média | 4h |
| 9 | **Stress Test** | k6 com 100+ VUs | Média | 4h |
| 10 | **GCloud Run otimizado** | Cold start, memória, min/max instances | Baixa | 2h |

## Prioridade imediata (Sprint v8.0)

1. FastAPI (substitui Flask)
2. Redis cache (performance)
3. PostgreSQL (escalabilidade)
4. Paginação e streaming
5. NGINX + stress test
