# SELIX — Backlog de Engenharia

## Objetivo

Vincular cada entrega à arquitetura, aos arquivos, às dependências,
aos testes e aos critérios verificáveis de aceite.

## Prioridades

- P0: integridade da base contábil e confiabilidade da extração.
- P1: fundamentos financeiros e modelo macroeconômico.
- P2: projeção, valuation, comparação e apresentação.

## Backlog

| ID | Entrega | Arquivos / áreas | Dependências | Testes | Aceite |
|---|---|---|---|---|---|
| SEL-001 | Persistência e inventário CVM | data/raw/cvm; scripts/import_cvm.py | Acesso aos arquivos DFP/ITR | Testes de inventário e hash | Arquivos copiados sem sobrescrita, inventariados e identificados |
| SEL-002 | Integridade e versões | src/selix/ingestion/validation.py | SEL-001 | CSV inválido, encoding, escala e hash | Origem, versão, escala e integridade verificáveis |
| SEL-003 | Extração DFP/ITR | src/selix/recovery/cvm_extract.py | SEL-002 | tests/recovery | Extração reproduzível por empresa e período |
| SEL-004 | Abertura e fechamento fiscal | recovery/cvm_extract.py | SEL-003 | Exercícios de março e dezembro; ÚLTIMO/PENÚLTIMO | Datas fiscais reais, sem presumir 31/12 |
| SEL-005 | Extração de juros | recovery/debt.py | SEL-003 | Contas de DRE e classificações | Juros identificados sem confundir câmbio e demais despesas |
| SEL-006 | Arrendamentos IFRS 16 | recovery/leases.py | SEL-003 | Contas de curto e longo prazo | Arrendamentos separados da dívida financeira |
| SEL-007 | Reconciliação de dívida e caixa | recovery/reconciliation.py | SEL-005, SEL-006 | Identidade de saldos e divergências | Saldos conciliados ou pendências explicitadas |
| SEL-008 | Demonstrações normalizadas | financials/ | SEL-003, SEL-007 | DRE, BP e DFC | Demonstrações com unidade, período e origem |
| SEL-009 | NOPAT e capital investido | valuation/nopat.py; invested_capital.py | SEL-008 | Fórmulas e casos de referência | Fórmulas e premissas documentadas |
| SEL-010 | ROIC histórico | valuation/returns.py | SEL-009 | Períodos, abertura e fechamento | ROIC calculado com capital médio e período identificado |
| SEL-011 | Séries Selic e Focus | macro/selic.py; focus.py | Fontes oficiais | Datas, revisões e ausência de dados | Observado separado de expectativa |
| SEL-012 | Motor macroeconômico | scenarios/engine.py; assumptions.py | SEL-011 | Cenários determinísticos | Cenários reproduzíveis e premissas explícitas |
| SEL-013 | Sensibilidade à Selic | scenarios/sensitivity.py | SEL-005, SEL-007, SEL-012 | Dívida prefixada e pós-fixada | Reprecificação somente da parcela exposta |
| SEL-014 | Eventos e reestruturações | companies/; evidencias/ | Fontes oficiais e RI | Identidade legal e datas | Eventos documentados com fonte e perímetro |
| SEL-015 | Projeção de cinco anos | scenarios/ | SEL-008, SEL-012, SEL-013 | Fluxo de caixa e dívida | Projeção reproduzível por cenário |
| SEL-016 | Valuation e valor terminal | valuation/valuation.py | SEL-009, SEL-010, SEL-015 | Sensibilidade e consistência | Premissas, taxa de desconto e terminal explícitos |
| SEL-017 | Comparação de empresas | reporting/; companies/ | SEL-014, SEL-016 | Períodos e perímetros comparáveis | Comparação não mistura entidades ou exercícios incompatíveis |
| SEL-018 | Relatório e dashboard | reporting/dashboard.py; export.py | SEL-017 | Testes de exportação | Relatório rastreável e reproduzível |

## Regras de priorização

1. SEL-001 a SEL-007 bloqueiam projeções financeiras confiáveis.
2. SEL-008 a SEL-010 formam a camada de fundamentos.
3. SEL-011 a SEL-013 conectam macroeconomia à estrutura de capital.
4. SEL-015 e SEL-016 dependem de dados e premissas validados.
5. SEL-017 e SEL-018 são entregas de apresentação, não substituem validação.

## Definition of Done

Um item só pode ser marcado como concluído quando:
- O código e os arquivos envolvidos existem.
- Os testes correspondentes passam.
- Os dados possuem origem e período identificados.
- As unidades e escalas estão documentadas.
- As limitações e exceções estão registradas.
- O critério de aceite foi demonstrado.

Código executando sem validação contábil não é suficiente para concluir
um item financeiro.

## Estado inicial conhecido

| Área | Estado informado |
|---|---|
| recovery/cvm_extract.py | Em desenvolvimento |
| tests/recovery/test_cvm_extract.py | Alterado; último resultado informado: 39 testes aprovados |
| Persistência CVM em data/raw | Aguardando confirmação |
| Extração de juros | Pendente |
| Extração IFRS 16 | Pendente |
| Reconciliação de dívida e caixa | Pendente |
| ROIC | Implementação inicial; proxy a validar |
| Séries e cenários Selic | Planejados |
| Valuation de cinco anos | Planejado |
| Dashboard comparativo | Planejado |

O estado acima é um registro de contexto de trabalho, não uma auditoria
executada nesta versão da documentação.
