# SELIX — Metodologia Financeira e Macroeconômica

## 1. Objetivo

Definir regras mínimas para transformar dados oficiais em indicadores,
cenários e valuation sem perder proveniência ou consistência contábil.

## 2. Fontes e proveniência

Cada observação deve registrar, quando aplicável:
- Fonte e URL ou identificação do arquivo.
- Data de publicação e data de referência.
- Empresa, CNPJ e CD_CVM.
- DFP ou ITR.
- Demonstração consolidada ou individual.
- Código e descrição da conta.
- Versão e ordem do exercício.
- Unidade e escala monetária.
- Data de ingestão e hash do arquivo.

Dados observados, expectativas e premissas devem ser armazenados e
apresentados separadamente.

## 3. Dados CVM

Arquivos CSV podem usar separador ponto e vírgula e encoding Latin-1.
A escala MIL deve ser convertida para unidade monetária multiplicando
o valor por 1.000.

A seleção deve considerar:
- CD_CVM.
- DT_REFER.
- DT_INI_EXERC e DT_FIM_EXERC.
- VERSAO.
- ORDEM_EXERC.
- CD_CONTA.
- ESCALA_MOEDA.

ÚLTIMO e PENÚLTIMO não substituem a identificação da data fiscal real.
O exercício de uma empresa que fecha em março não deve ser tratado como
se encerrasse em dezembro.

Não somar conta-pai com suas contas-filhas.

## 4. Perímetro societário

GPA, Raízen Energia, Raízen S.A. e Petrobras não devem ser tratados como
entidades equivalentes.

Antes de comparar:
- Confirmar CD_CVM e CNPJ.
- Confirmar demonstração consolidada ou individual.
- Confirmar controladas e perímetro.
- Confirmar data de fechamento.
- Registrar mudanças societárias relevantes.

## 5. Dívida e caixa

Separar:
- Empréstimos e financiamentos de curto prazo.
- Empréstimos e financiamentos de longo prazo.
- Arrendamentos IFRS 16.
- Caixa e equivalentes.
- Aplicações financeiras.
- Outros passivos financeiros.
- Dívida sujeita a reestruturação, quando identificável.

Dívida financeira não deve ser confundida com dívida agregada incluindo
arrendamentos.

A dívida líquida deve declarar sua definição e os componentes de caixa
deduzidos.

Valores ausentes não devem ser convertidos silenciosamente em zero.

## 6. Despesas financeiras

A conta agregadora de despesas financeiras pode incluir juros, variação
cambial e outros custos.

A classificação deve buscar:
- Despesas de juros.
- Encargos de empréstimos.
- Custos de arrendamento.
- Variação cambial.
- Outros encargos financeiros.

Não classificar toda a conta de despesas financeiras como juros sem
reconciliação com notas explicativas ou detalhamento adequado.

## 7. Capital investido e ROIC

O capital investido deve ter definição explícita e consistente.

A implementação deve documentar:
- Ativos operacionais considerados.
- Passivos operacionais deduzidos.
- Dívida e arrendamentos incluídos ou excluídos.
- Patrimônio líquido e ajustes.
- Critério de abertura, fechamento e média.

ROIC = NOPAT / Capital Investido Médio.

NOPAT depende de resultado operacional ajustado e tratamento tributário
coerente. A conta contábil de resultado antes do financeiro e tributos
não é automaticamente EBIT operacional puro.

Anualização linear de um período parcial é extrapolação, não retorno
anual realizado. Deve ser identificada como estimativa.

## 8. Selic e transmissão financeira

A Selic não reduz automaticamente o custo de toda a dívida.

A sensibilidade deve considerar:
- Indexador contratual.
- Parcela pós-fixada.
- Parcela prefixada.
- Moeda e exposição cambial.
- Hedge.
- Spread de crédito.
- Vencimento e data de refinanciamento.
- Frequência de reajuste.

A cadeia econômica a modelar é:

despesa financeira -> lucro -> caixa e FCF -> amortização -> dívida líquida
-> risco de refinanciamento -> valuation.

## 9. Cenários macroeconômicos

Horizontes de análise:
- 1 ano: liquidez e vencimentos.
- 3 anos: reestruturação e custo da dívida.
- 5 anos: cenário principal de caixa e valuation.
- 10 anos: teste estrutural e valor terminal.

Cenários mínimos:
- Pessimista.
- Base.
- Otimista.
- Choque de juros.

Expectativas Focus devem carregar a data da pesquisa. Não são garantias
nem decisões do COPOM.

Uma hipótese alternativa de Selic a 7,5% em 12 meses deve ser identificada
como cenário próprio, não como consenso de mercado.

A janela 2019–2024 pode ser usada para estudar juros baixos e o ciclo
posterior de alta. Não atribuir toda a dinâmica econômica exclusivamente
à pandemia.

## 10. Projeção e valuation

Projeções devem explicitar:
- Receita e crescimento.
- Margens.
- CAPEX.
- Capital de giro.
- Impostos.
- Dívida e custo por indexador.
- Amortizações e refinanciamentos.
- Caixa e fluxo de caixa livre.
- Taxa de desconto.
- Valor terminal.

Não preencher dados históricos ausentes com projeções sem identificá-las.

## 11. Reestruturações

Recuperação extrajudicial não deve ser descrita como recuperação judicial.
Registrar:
- Data do evento.
- Entidade abrangida.
- Créditos sujeitos.
- Credores e garantias.
- Conversões, descontos e reperfilamento.
- Aportes e condições.
- Situação de implementação.
- Fonte documental.

Homologação ou anúncio de plano não comprova recuperação operacional.

## 12. Evidências e auditoria

Cada cálculo relevante deve ser reproduzível e rastreável até:
1. Arquivo de origem.
2. Linha ou conta.
3. Transformação aplicada.
4. Unidade e escala.
5. Fórmula.
6. Teste correspondente.

Divergências devem ser registradas, nunca ocultadas por ajustes silenciosos.
