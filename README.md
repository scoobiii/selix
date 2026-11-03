# SELIX — modelo econômico com dados oficiais

O SELIX calcula indicadores do modelo e publica a observação da Selic obtida no Banco Central do Brasil. Valores operacionais não devem ser copiados manualmente para esta documentação.

## Fonte oficial e valores atuais

O snapshot histórico é gerado pelo [workflow de publicação](.github/workflows/bluesky_ci.yml) e validado pelo [workflow de testes](.github/workflows/tests.yml), com o resultado versionado no [snapshot oficial](public/selix-official.json). O snapshot inclui a série de origem, data da observação, instante de geração, parâmetros do modelo, diferencial calculado e hash de integridade.

- [Snapshot histórico em JSON](public/selix-official.json)
- [API pública do Banco Central — SGS](https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?dataInicial=03/11/2016)
- [Workflow de validação](.github/workflows/tests.yml)
- [Workflow de publicação](.github/workflows/bluesky_ci.yml)

## Contrato de dados

- A Selic observada deve vir exclusivamente da série SGS de meta Selic.
- A Selic ideal e os parâmetros associados são calculados pelo núcleo do modelo.
- O diferencial é sempre calculado como selic_atual menos selic_ideal.
- Não são permitidos fallbacks numéricos, dados sem data de observação ou snapshots sem proveniência.
- Se a API oficial falhar, os dados forem inválidos ou os artefatos divergirem, o CI deve falhar e a publicação deve ser bloqueada.

## CI e publicação

O CI valida o código e gera um artefato histórico identificado como tal. O publicador do Bluesky consulta o SPI e o BCB em runtime; se a fonte falhar, a publicação é bloqueada.

## Limitações

O resultado é uma estimativa de modelo para apoio à decisão. Não representa orientação oficial do Banco Central nem substitui decisões do COPOM.

## SELIX Recovery — análise financeira baseada em dados CVM

O SELIX Recovery amplia o projeto com análise histórica de demonstrações
financeiras DFP/ITR da CVM. Esta camada é implementada em Python e deve ser
distinguida do pacote JavaScript `selix-core`.

### Funcionalidades implementadas na branch de desenvolvimento

- Extração de demonstrações financeiras por empresa e exercício fiscal.
- Identificação de despesas financeiras com tratamento de variações de
  descrição encontradas nos arquivos da CVM.
- Sinalização quando o resultado financeiro existe, mas a conta de despesa
  detalhada não está disponível.
- Cálculo de cobertura de juros, respeitando a disponibilidade e a
  classificação contábil das contas.
- Análise de sensibilidade da dívida.
- Reconciliação da variação do patrimônio líquido com o lucro líquido,
  sinalizando resíduos não explicados.

### Integridade e interpretação

- Ausência de abertura contábil não deve ser preenchida por estimativas
  apresentadas como valores observados.
- Resultado financeiro não equivale necessariamente a juros.
- O resíduo de patrimônio líquido pode incluir dividendos, aportes,
  outros resultados abrangentes, reclassificações e mudanças de perímetro.
- Alertas indicam necessidade de investigação; não provam isoladamente
  uma causa econômica.
- Períodos fiscais e perímetros societários devem permanecer explícitos.

### Limites atuais

O Recovery está em desenvolvimento na branch `feat/selix-recovery-model`.
A persistência transacional multiempresa, uma API pública própria e os
dashboards universais ainda não devem ser considerados entregas concluídas.

Consulte o [backlog de engenharia](docs/backlog.md) para o estado e os
próximos critérios de aceite.

## Desenvolvimento

Instale as dependências listadas em requirements.txt e execute pytest. Testes unitários devem simular respostas da API; dados simulados não podem ser apresentados como observações atuais.
