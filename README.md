# SELIX

**Modelo econômico determinístico e ferramentas de pesquisa para o Brasil.** Este repositório reúne uma aplicação Python e um pacote JavaScript independente. Eles têm escopos diferentes; não confunda um cálculo do modelo com a taxa Selic observada pelo Banco Central.

## Para quem é

- **Investidores e rentistas:** explore cenários e compare a taxa ideal calculada pelo modelo com uma taxa de mercado obtida e verificada separadamente. O SELIX não recomenda comprar, vender ou manter ativos.
- **Trabalhadores e público geral:** veja quais hipóteses entram no cálculo e como mudar inflação esperada, prêmio de risco, credibilidade e hiato do produto altera o resultado. Isto não é aconselhamento financeiro pessoal.
- **Desenvolvedores e agentes de software/IA:** use entradas explícitas e uma saída JSON reproduzível. Não invente uma Selic atual nem forneça uma taxa atual sem validar fonte, série e data.

## O que há neste repositório
O snapshot histórico é gerado pelo [workflow de publicação](.github/workflows/bluesky_ci.yml) e validado pelo [workflow de testes](.github/workflows/tests.yml), com o resultado versionado no [snapshot oficial](public/selix-official.json). O snapshot inclui a série de origem, data da observação, instante de geração, parâmetros do modelo, diferencial calculado e hash de integridade.

- [Snapshot histórico em JSON](public/selix-official.json)
- [API pública do Banco Central — SGS](https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?dataInicial=03/11/2016)
- [Workflow de validação](.github/workflows/tests.yml)
- [Workflow de publicação](.github/workflows/bluesky_ci.yml)

| Componente | Local | O que faz | O que não faz |
| --- | --- | --- | --- |
| Aplicação Python | `src/` | API e ferramentas de pesquisa do SELIX; o fluxo operacional de dados atuais usa o SPI e a série de meta Selic SGS 432 do Banco Central. | Não é, neste momento, um pacote Python instalável com `pip install selix`. |
| SELIX Core para Node.js | [`packages/selix-core`](packages/selix-core/README.md) | Implementa em JavaScript o núcleo determinístico de cálculo, sem dependências de execução. | Não consulta o Banco Central, não valida proveniência de dados atuais e não fornece recomendações financeiras. |

O pacote `selix-core` está em desenvolvimento. **Ele ainda não está publicado no npm Registry**: a verificação do nome `selix-core` retornou `404 Not Found`. O workflow [`npm-package.yml`](.github/workflows/npm-package.yml) executa testes, verifica o conteúdo do tarball e faz um smoke test da CLI; não publica no npm.

## Começar com o SELIX Core

Requisitos: Node.js 20 ou superior. Clone o repositório e rode os comandos a partir do diretório do pacote:

```bash
git clone https://github.com/scoobiii/selix.git
cd selix/packages/selix-core
node --version
npm test
npm pack --dry-run
printf '%s\n' '{"inputs":{"inflacaoEsperada":4.48,"premioRisco":1.25,"credibilidade":0.5,"gapProduto":0.5}}' | node bin/selix-core.js
```

O exemplo usa somente o cálculo local. Com esses valores, o modelo retorna `selic_ideal_quantizada: 7`, `selic_atual: null` e `diferencial_pp: null`. Os valores decimais de taxas e inflação estão em **pontos percentuais**: `4.48` significa 4,48%, não `0.0448`.

Para importar o pacote de outro projeto enquanto ele ainda não estiver publicado, instale a pasta local do clone:

```bash
npm install /caminho/para/selix/packages/selix-core
```

Depois, use-o como módulo ES:

```js
import { calcularSelix } from "selix-core";

const resultado = calcularSelix({
  inflacaoEsperada: 4.48,
  premioRisco: 1.25,
  credibilidade: 0.5,
  gapProduto: 0.5,
});

console.log(resultado.selic_ideal_quantizada); // 7
console.log(resultado.selic_atual);             // null: não foi informada
```

Consulte o [guia completo do pacote](packages/selix-core/README.md) para entradas opcionais, CLI, fórmula e mensagens de erro. **Não use `npm install selix-core` antes de uma versão aparecer no registro público.**

## Como interpretar os resultados

O `selic_ideal_quantizada` é uma saída do modelo, arredondada para baixo na grade de 0,25 ponto percentual definida pelo pacote. Não é uma decisão do COPOM nem uma cotação atual. Por padrão, o pacote JavaScript devolve `selic_atual` e `diferencial_pp` como `null`.

A opção `selicAtual` só deve ser usada quando o sistema chamador tiver obtido e validado independentemente a observação, a fonte oficial, a série e a data. O pacote JavaScript não verifica esses dados. O fluxo Python de dados atuais tem outro escopo; consulte o [contrato de dados oficiais](docs/SELIX_ESCOPO.md) e leia a data/proveniência do [snapshot versionado](public/selix-official.json), que não deve ser tratado como feed ao vivo.

O SELIX é uma ferramenta de análise e pesquisa, não é orientação financeira, promessa de rentabilidade, previsão garantida ou substituto de revisão profissional.

## Aplicação Python

A aplicação Python usa as dependências de [`requirements.txt`](requirements.txt). Para instalação, inicialização, banco de dados e execução dos testes, siga o fluxo versionado em [`.github/workflows/tests.yml`](.github/workflows/tests.yml), que configura Python, Redis, banco de teste e testes de API separadamente. O repositório não declara um pacote Python raiz em `pyproject.toml` ou `setup.py`; portanto, não instale o projeto com `pip install selix`.

## Testes do pacote JavaScript

A partir de `packages/selix-core`:

```bash
npm test
npm pack --dry-run
printf '%s\n' '{"inputs":{"inflacaoEsperada":4.48,"premioRisco":1.25,"credibilidade":0.5,"gapProduto":0.5}}' | node bin/selix-core.js
```

Estes são os checks do workflow do pacote, além do smoke test da CLI. O repositório também possui testes Python; eles não são substituídos pelos testes do pacote npm.

## Contribuir

Mudanças são propostas por Pull Request: crie uma branch, faça commits nela, rode os testes apropriados e abra um PR contra `main`. Veja [`CONTRIBUTING.md`](CONTRIBUTING.md), o [workflow de testes](.github/workflows/tests.yml) e o [workflow do pacote npm](.github/workflows/npm-package.yml). Não envie diretamente para `main`.
