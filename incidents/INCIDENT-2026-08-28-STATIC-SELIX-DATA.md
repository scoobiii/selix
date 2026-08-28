# INCIDENT-2026-08-28 — SELIX: dado estático promovido a estado atual

**Severidade:** GRAVE
**Status:** corrigido no código operacional; limpeza/migração de referências legadas continua controlada

## O que aconteceu

Uma integração externa reproduziu uma peça/fixture de teste que continha `SELIC atual = 14,25%` e `SELIC ideal = 9,25%`. Esses números eram adequados apenas ao contexto histórico daquela execução.

O erro arquitetural foi permitir que valores de uma prova/fixture histórica ocupassem o mesmo espaço semântico de dados CURRENT. Um consumidor LLM pode recuperar um número antigo e apresentá-lo como atual sem ter como inferir a intenção humana do arquivo.

**Responsabilidade:** a integração que preparei para o Vortex cometeu esse erro ao transformar a prova histórica em fixture operacional. O Vortex é outro sprint; este incidente e a correção pertencem ao SELIX.

## Regra nova — sem exceção

1. `SELIC atual` é **SPI-owned**.
2. O valor atual deve ser obtido em runtime pelo **BCB SGS série 432**.
3. Caller, fixture, prompt, arte ou arquivo estático não pode fornecer `selic_atual`.
4. `selic_ideal` operacional vem do modelo canônico atual do SELIX; não pode ser injetada pelo caller.
5. Dados históricos não ficam no namespace operacional. Quando necessários para auditoria, ficam em `archive/historical/` e não são fonte de CURRENT.
6. Qualquer provenance diferente de `runtime:BCB SGS 432` é REJECT para uma operação CURRENT.
7. Um snapshot publicado como `public/selix-official.json` é artefato de publicação; não substitui a busca dinâmica do BCB durante uma execução.

## Implementação

- `src/selix/spi.py` é a autoridade operacional para CURRENT.
- `src/providers/bcb_provider.py` continua sendo o acesso ao BCB e a série 432. O provider já não contém número discricionário. 
- `src/core/selic_prover.py` foi substituído: não contém mais a tese operacional de 9,25%; delega ao modelo canônico atual.
- `tests/test_spi_current.py` verifica rejeição de `selic_atual`/`selic_ideal` injetados e exige BCB SGS 432 + provenance de runtime.
- `tests/test_integrado.py` deixou de esperar a constante histórica 9,25%.
- `lean_proof/SELIX_v4.lean` foi removido do namespace operacional e colocado em quarentena histórica.

## Fonte canônica atual

`public/selix-official.json` registra atualmente `selic_atual = 14,00%`, `selic_ideal = 8,25%`, fonte `BCB SGS 432`, série 432 e data BCB 15/08/2026. Ele é um snapshot de publicação; a execução CURRENT deve consultar o BCB em runtime. 

## Critério de aceitação

Uma execução CURRENT só pode sair como válida se tiver:

```text
status = current
selic_atual_serie = 432
selic_atual_fonte = BCB SGS 432
provenance = runtime:BCB SGS 432
fetched_at = timestamp da execução
```

Qualquer artefato que diga `SELIC ATUAL = X` sem essa proveniência deve ser rejeitado.

## Não fazer

- Não colocar números atuais em `input.json`.
- Não usar prova histórica como fixture de CURRENT.
- Não confiar no LLM para decidir se um número é histórico ou atual.
- Não usar `selix-official.json` como cache eterno de mercado.
- Não apagar evidência histórica e depois reutilizá-la no contexto operacional; a separação é física/semântica.
