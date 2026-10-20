# SELIX — modelo econômico com dados oficiais

O SELIX calcula indicadores do modelo e publica a observação da Selic obtida no Banco Central do Brasil. Valores operacionais não devem ser copiados manualmente para esta documentação.

## Fonte oficial e valores atuais

Os valores operacionais são derivados pelo CI Runner e publicados no [snapshot oficial](public/selix-official.json). O snapshot inclui a série de origem, data da observação, instante de geração, parâmetros do modelo, diferencial calculado e hash de integridade.

- [Snapshot histórico em JSON](public/selix-official.json)
- [API pública do Banco Central — SGS](https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados)
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

## Desenvolvimento

Instale as dependências listadas em requirements.txt e execute pytest. Testes unitários devem simular respostas da API; dados simulados não podem ser apresentados como observações atuais.
