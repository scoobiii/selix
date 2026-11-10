# SELIX Core para Node.js

**Pacote npm experimental (`0.1.0`) com o núcleo determinístico de cálculo do SELIX em JavaScript.** Requer Node.js 20 ou superior e não tem dependências de execução.

> **Situação:** `selix-core` ainda não está publicado no npm Registry. O workflow deste repositório testa e empacota o código, mas não publica uma versão. Não conte com `npm install selix-core` ou `npx selix-core` até que o pacote esteja disponível no registro.

## O que este pacote faz

Recebe hipóteses econômicas declaradas por quem o chama e calcula resultados do modelo, incluindo uma Selic ideal contínua e quantizada. É útil para explorar cenários, integrar o cálculo num aplicativo ou fornecer uma saída JSON estruturada a uma automação.

- **Investidores e rentistas:** compare cenários do modelo com dados de mercado verificados por sua própria aplicação; o pacote não diz se deve comprar, vender ou manter um ativo.
- **Trabalhadores e público geral:** inspecione as hipóteses e os resultados sem tratar uma taxa calculada como decisão oficial ou recomendação pessoal.
- **Agentes de software/IA:** envie valores explícitos e leia o JSON retornado. Não invente uma Selic observada nem a marque como atual sem validação externa.

Este pacote **não** busca dados do BCB ou de outros provedores, não valida proveniência da taxa informada, não chama um LLM e não fornece aconselhamento financeiro.

## Instalação

Antes da publicação no npm, instale a pasta local do clone em seu projeto Node.js:

```bash
npm install /caminho/para/selix/packages/selix-core
```

Substitua o caminho pelo local do clone. Após instalar, importe a API com módulos ES:

```js
import { calcularSelix } from "selix-core";
```

Quando uma versão estiver efetivamente publicada, a instalação pelo registro será `npm install selix-core`.

## Exemplo: cálculo básico

As taxas abaixo são expressas em **pontos percentuais (p.p.)**: `4.48` representa 4,48%, não `0.0448`. `credibilidade` é um parâmetro positivo, sem unidade. A biblioteca valida entradas numéricas finitas e exige credibilidade maior que zero.

```js
import { calcularSelix } from "selix-core";

const entradas = {
  inflacaoEsperada: 4.48,
  premioRisco: 1.25,
  credibilidade: 0.5,
  gapProduto: 0.5,
};

const resultado = calcularSelix(entradas);

console.log(resultado.selic_ideal_quantizada); // 7
console.log(resultado.selic_atual);             // null
console.log(resultado.diferencial_pp);          // null
```

Com essas entradas e os parâmetros energéticos padrão, o cálculo retorna `tau = 0.7786`, juro real necessário de `7.23` p.p. e Selic ideal quantizada de `7.00` p.p. A quantização usa a grade de 0,25 p.p. (`COPOM_GRID`) e arredonda para baixo.

## Taxa observada e diferencial

`selicAtual` é opcional e fica `null` por padrão. Só informe uma taxa que seu sistema tenha obtido e validado de forma independente, incluindo a fonte oficial, a série e a data da observação. Esta biblioteca não faz essa verificação.

```js
const resultado = calcularSelix(entradas, { selicAtual: 14.25 });

console.log(resultado.selic_atual);    // 14.25: valor fornecido pelo chamador
console.log(resultado.diferencial_pp);  // 7.25: selicAtual - selic_ideal_quantizada
```

O exemplo demonstra a API, não afirma que `14.25` seja a taxa atual. Não passe esse campo quando não puder validar o dado; nesse caso, deixe-o ausente e ambos os campos de valor atual/diferencial permanecem `null`.

## Entradas opcionais

`calcularSelix(entradas, opcoes)` aceita:

| Opção | Tipo/unidade | Padrão | Descrição |
| --- | --- | --- | --- |
| `selicAtual` | número em p.p. ou `null` | `null` | Observação externa validada pelo chamador; não é buscada nem autenticada pelo pacote. |
| `choqueEnergia` | número em p.p. | `0` | Choque utilizado para calcular a inflação efetiva. |
| `mix.etanolGasolina` | percentual de 0 a 100 | `32` | Percentual de etanol na gasolina. |
| `mix.biodieselDiesel` | percentual de 0 a 100 | `15` | Percentual de biodiesel no diesel. |
| `mix.pesoGasolina` | número não negativo | `0.42` | Peso da gasolina no cálculo da transmissão energética. |
| `mix.pesoDiesel` | número não negativo | `0.58` | Peso do diesel no cálculo da transmissão energética. |

Exemplo:

```js
const cenario = calcularSelix(entradas, {
  choqueEnergia: 1,
  mix: {
    etanolGasolina: 35,
    biodieselDiesel: 20,
    pesoGasolina: 0.42,
    pesoDiesel: 0.58,
  },
});
```

As funções exportadas também incluem `calcularTau(mix)`, `quantizarCopom(valor, grid)` e `calcularJuroRealNecessario(entradas, opcoes)`. Veja as assinaturas em [`src/index.d.ts`](src/index.d.ts).

## CLI para scripts e agentes

A CLI lê uma requisição JSON pela entrada padrão e escreve `{ "ok": true, "result": ... }` em caso de sucesso. Erros são escritos como JSON no `stderr`, com status de saída diferente de zero.

No clone do repositório, execute:

```bash
cd packages/selix-core
printf '%s\n' '{"inputs":{"inflacaoEsperada":4.48,"premioRisco":1.25,"credibilidade":0.5,"gapProduto":0.5}}' | node bin/selix-core.js
```

Formato aceito:

```json
{
  "inputs": {
    "inflacaoEsperada": 4.48,
    "premioRisco": 1.25,
    "credibilidade": 0.5,
    "gapProduto": 0.5
  },
  "options": {
    "choqueEnergia": 0
  }
}
```

`options` é opcional e pode conter `mix`, `choqueEnergia` e `selicAtual`. A CLI não consulta dados ao vivo; agentes devem manter separados o cálculo do modelo e qualquer dado observado que tenham validado.

## Como o modelo calcula

O core espelha funções determinísticas do SELIX em Python. Em termos simplificados:

```text
tau = clamp(1 - (pesoGasolina × etanol_pct/100 + pesoDiesel × biodiesel_pct/100), 0, 1)
inflacao_efetiva = inflacaoEsperada + tau × choqueEnergia
juro_real_necessario = inflacao_efetiva + premioRisco / credibilidade + 0.5 × gapProduto
selic_ideal_quantizada = arredondar_para_baixo(juro_real_necessario, grade=0.25 p.p.)
```

O resultado contém as hipóteses recebidas, parâmetros energéticos, `tau`, inflação efetiva, juro real necessário, Selic ideal contínua e quantizada, além de `selic_atual` e `diferencial_pp` quando uma taxa observada é fornecida.

## Testes e desenvolvimento

A partir de `packages/selix-core`:

```bash
npm test
npm pack --dry-run
```

O primeiro comando roda os testes nativos de Node.js e os vetores de referência compartilhados com Python; o segundo confere os arquivos incluídos no tarball. O pacote ainda não garante equivalência bit a bit para todas as bordas de ponto flutuante. Use os testes de paridade e revisão apropriada antes de uma versão estável `1.0.0`.

## Limitações e uso responsável

- Uma saída `selic_ideal_quantizada` é resultado de um modelo, não uma observação atual da Selic, decisão do COPOM ou previsão garantida.
- A biblioteca não faz avaliação de perfil, risco pessoal, horizonte de investimento, tributação ou adequação de carteira.
- As decisões e a validação dos dados fornecidos — inclusive `selicAtual` — são responsabilidade do sistema chamador.
- O resultado serve para análise e pesquisa; não é aconselhamento financeiro nem substitui análise profissional.

Licença: MIT. Código-fonte e histórico: [github.com/scoobiii/selix](https://github.com/scoobiii/selix).
