# SELIX — CURRENT DATA POLICY

## Autoridade

Para dados de mercado atuais, a única autoridade operacional é o SPI do SELIX.

```text
caller / LLM / arte / README / few-shot / fixture
                    │
                    X  não é fonte CURRENT
                    │
                    ▼
             SELIX SPI
                    │
                    ▼
             BCB SGS 432
                    │
                    ▼
             CURRENT snapshot
```

## Contrato

`selic_atual`, `selic_ideal` e `diferencial` são campos pertencentes ao SPI quando usados como estado CURRENT. O caller não pode fornecê-los.

A Selic atual precisa conter:

- `status: current`
- `selic_atual_serie: 432`
- `selic_atual_fonte: BCB SGS 432`
- `provenance: runtime:BCB SGS 432`
- data da observação do BCB
- instante de coleta (`fetched_at`)

## Falha fechada

BCB indisponível, série diferente, provenance inválida ou dado stale ⇒ **REJECT**.

Não existe fallback numérico hardcoded.

## Histórico

Material histórico não participa do contexto operacional padrão. Ele deve ser arquivado fora de `src/`, `scripts/` e `SelixModelfile` e não pode ser usado para preencher um campo CURRENT.

A existência de um número antigo em Git history não autoriza seu uso em runtime.

## Modelo

O `core.py` calcula a Selic ideal. Ele não é fonte de mercado e não deve conter default numérico para a Selic atual.

## Publicação

Qualquer arte, post ou relatório que use a etiqueta **ATUAL/CURRENT** deve ser construído a partir de um snapshot CURRENT recém-validado pelo SPI.

## Princípio

> **LLM não decide se um número é atual. O runtime decide.**
