# SELIX — Política de Dados CURRENT

## Regra de ouro

**LLM não decide se um número é atual. O runtime decide.**

Para qualquer saída com o rótulo `ATUAL`, o SELIX deve buscar a fonte dinâmica autorizada durante a execução e anexar provenance verificável.

## Autoridade

- **SELIC atual:** BCB SGS série 432, obtida em runtime.
- **SELIC ideal:** modelo canônico carregado pelo SELIX (`src.selix.config` → core atual).
- **Diferencial:** derivado em runtime (`atual - ideal`).
- `public/selix-official.json`: snapshot de publicação, útil para distribuição/consulta, mas não é cache eterno da taxa de mercado.

## Proibido

```text
input.json → selic_atual
prompt → selic_atual
arte → selic_atual
fixture → selic_atual
prova histórica → selic_atual
constante hardcoded → selic_atual
```

Qualquer tentativa de injeção deve resultar em `REJECT`.

## Isolamento histórico

Material superseded que contém valores que já não representam o modelo/mercado atual deve ficar fora do namespace operacional em `archive/historical/<data>/`.

Histórico não é apagado por ser histórico; ele é **retirado da rota de execução e recuperação operacional**.

## Provenance mínima de CURRENT

```json
{
  "status": "current",
  "selic_atual_serie": 432,
  "selic_atual_fonte": "BCB SGS 432",
  "provenance": "runtime:BCB SGS 432",
  "fetched_at": "<timestamp>"
}
```

Sem todos esses elementos, uma saída `ATUAL` não é válida.

## Incidente que motivou a política

Em 28/08/2026, uma integração que preparei para o Vortex promoveu uma fixture histórica com `14,25%` / `9,25%` para um contexto operacional. Isso permitiu que um consumidor LLM recuperasse dados superseded como se fossem atuais.

A correção foi feita no **SELIX**: SPI dinâmico, rejeição de campos caller-owned, remoção da prova legada do namespace operacional e testes de regressão. O trabalho de integração do Vortex permanece em outro sprint.
