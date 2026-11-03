# SELIX — Plano de Sprints

## Estratégia

Executar em sequência dependente. Não avançar para valuation enquanto
os dados financeiros críticos não estiverem reconciliados.

## Sprint 0 — Preservação e diagnóstico

**Objetivo:** conhecer o estado real do repositório e dos dados.

Entregas:
- Inventário de arquivos DFP/ITR em /tmp/cvm.
- Cópia não destrutiva para data/raw/cvm.
- Manifesto SHA-256.
- Inspeção dos diffs existentes.
- Baseline dos testes.
- Documentação de arquitetura, backlog, sprints e metodologia.

Arquivos:
- data/raw/cvm/
- evidencias/cvm/
- docs/architecture.md
- docs/backlog.md
- docs/sprint_plan.md
- docs/methodology.md

Aceite:
- Dados inventariados.
- Nenhum original sobrescrito.
- Alterações preexistentes preservadas.
- Resultado dos testes registrado com data e comando.

## Sprint 1 — CVM e extração confiável

**Objetivo:** padronizar a leitura de DFP e ITR.

Entregas:
- Encoding, separador e escala monetária.
- Identificação de CD_CVM e demonstração consolidada/individual.
- Tratamento de ÚLTIMO e PENÚLTIMO.
- Abertura e fechamento pelo DT_FIM_EXERC.
- Tratamento de exercícios fiscais de março e dezembro.
- Testes de regressão.

Arquivos:
- src/selix/ingestion/
- src/selix/recovery/cvm_extract.py
- tests/ingestion/
- tests/recovery/

Aceite:
- Período, entidade, versão e escala identificados.
- Sem duplicidade entre contas agregadoras e filhas.
- GPA, Raízen Energia e Petrobras identificadas pelo CD_CVM correto.

## Sprint 2 — Dívida, juros e arrendamentos

**Objetivo:** reconciliar a estrutura financeira.

Entregas:
- Classificação de despesas financeiras.
- Separação de juros, câmbio e outros custos.
- Separação de dívida financeira e IFRS 16.
- Identificação de caixa e aplicações.
- Reconciliação entre contas e notas explicativas.
- Registro de divergências.

Arquivos:
- src/selix/recovery/debt.py
- src/selix/recovery/leases.py
- src/selix/recovery/reconciliation.py
- tests/recovery/
- evidencias/reconciliation/

Aceite:
- Nenhum valor ausente convertido silenciosamente em zero.
- Juros e arrendamentos identificados ou marcados como pendentes.
- Diferenças de perímetro e classificação documentadas.

## Sprint 3 — Fundamentos e ROIC

**Objetivo:** construir métricas financeiras comparáveis.

Entregas:
- DRE, balanço e fluxo de caixa normalizados.
- EBIT operacional ajustado.
- NOPAT.
- Capital investido de abertura, fechamento e médio.
- ROIC por período.
- Identificação de itens não recorrentes.
- Anualização claramente separada do resultado observado.

Arquivos:
- src/selix/financials/
- src/selix/valuation/
- tests/financials/
- tests/valuation/

Aceite:
- Cada indicador tem fórmula, período, unidade e proveniência.
- Proxy não é apresentado como indicador definitivo.
- ROIC de períodos diferentes não é comparado sem ajuste.

## Sprint 4 — Selic e cenários macroeconômicos

**Objetivo:** modelar trajetórias macroeconômicas.

Entregas:
- Série histórica observada da Selic.
- Expectativas Focus com data de publicação.
- Inflação e câmbio.
- Cenários pessimista, base, otimista e choque de juros.
- Cenário alternativo de Selic a 7,5%, identificado como hipótese atribuída
  a André Lara Resende, não como consenso.

Arquivos:
- src/selix/macro/
- src/selix/scenarios/assumptions.py
- tests/macro/
- tests/scenarios/

Aceite:
- Observações, expectativas e hipóteses não são misturadas.
- Cada cenário pode ser reproduzido a partir das premissas registradas.

## Sprint 5 — Projeção e valuation

**Objetivo:** projetar cinco anos com estrutura financeira explícita.

Entregas:
- Receita, margens, CAPEX e capital de giro.
- Dívida por indexador, moeda, hedge e vencimento.
- Reprecificação e refinanciamento.
- Amortizações e caixa.
- Fluxo de caixa livre.
- Valuation e valor terminal.
- Sensibilidades.

Arquivos:
- src/selix/scenarios/engine.py
- src/selix/scenarios/sensitivity.py
- src/selix/valuation/valuation.py
- tests/scenarios/
- tests/valuation/

Aceite:
- Selic só afeta a parcela efetivamente exposta.
- Dívida prefixada não recebe redução automática de custo.
- Premissas e sensibilidades são rastreáveis.

## Sprint 6 — Empresas e painel comparativo

**Objetivo:** comparar recuperação, risco e retorno.

Entregas:
- GPA e sua reestruturação extrajudicial.
- Raízen com separação de entidades e perímetros.
- Petrobras como referência comparativa.
- Matriz de cinco períodos anteriores e posteriores aos eventos.
- Relatórios e dashboard.

Arquivos:
- src/selix/companies/
- src/selix/reporting/
- evidencias/sources/
- tests/

Aceite:
- Comparação respeita datas fiscais e perímetros societários.
- Períodos ainda não publicados são identificados como indisponíveis.
- Nenhuma projeção é apresentada como dado realizado.

## Gates entre sprints

- Sprint 0 -> 1: inventário e baseline registrados.
- Sprint 1 -> 2: extração fiscal validada.
- Sprint 2 -> 3: dívida, juros e arrendamentos reconciliados ou pendências
  explicitamente quantificadas.
- Sprint 3 -> 4: fundamentos financeiros documentados.
- Sprint 4 -> 5: cenários macroeconômicos reproduzíveis.
- Sprint 5 -> 6: projeções e valuation auditáveis.

## Proteção operacional

Não executar reset, clean, rebase destrutivo, commit ou push sem autorização.
Preservar:
- public/selix-official.json
- selix-official.json
- Alterações locais preexistentes em recovery e testes.

A documentação não autoriza alterações nesses arquivos.
