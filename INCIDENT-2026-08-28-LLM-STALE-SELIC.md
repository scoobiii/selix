# INC-2026-08-28 — LLM induzido por dados Selic obsoletos

## Resumo

Uma peça visual foi gerada com valores antigos de Selic. A causa não foi falta de fonte oficial: o repositório continha **few-shot operacional** ensinando explicitamente ao modelo que valores antigos eram a resposta para perguntas CURRENT.

O principal vetor encontrado foi `SelixModelfile`, que continha exemplos como:

- "Qual a Selic ideal?" → valor fixo antigo
- "Atualmente está em ..." → valor fixo antigo

Também havia scripts e documentos com os mesmos números. Isso criou concorrência semântica entre dados históricos e o estado atual.

## Causa raiz

O SELIX misturava três coisas que deveriam ser separadas:

1. **modelo** — calcula a Selic ideal;
2. **fonte CURRENT** — BCB SGS 432 em runtime;
3. **material histórico/editorial** — provas, posts e artes antigas.

Um LLM não pode ser encarregado de decidir sozinho qual delas é autoridade para uma pergunta CURRENT.

## Correção

- `SelixModelfile` não contém mais few-shot com taxas de mercado.
- `src/selix/spi.py` é a porta de autoridade CURRENT.
- `selic_atual` não possui default numérico no core.
- `scripts/postar_correcao.py` busca o SPI antes de publicar.
- O SPI rejeita `selic_atual`, `selic_ideal` e `diferencial` enviados pelo caller.
- Provenance CURRENT obrigatória: `runtime:BCB SGS 432`.
- Teste de regressão bloqueia valores legados no contexto operacional.

## Regra permanente

> **LLM não decide se um número é atual. O runtime decide.**

Se a fonte CURRENT não puder ser verificada, a operação deve falhar. Nunca reutilizar um número antigo como fallback silencioso.

## Evidência

O snapshot publicado `public/selix-official.json` identifica a fonte da Selic como BCB SGS 432 e o estado publicado vigente. O BCB também publicou a decisão de agosto de 2026 reduzindo a Selic para 14,00% a.a.

## O que não fazer

- não colocar taxa de mercado em Modelfile/few-shot;
- não colocar `selic_atual` em fixture de entrada;
- não usar README/post/arte como fonte de CURRENT;
- não chamar uma prova histórica de estado atual;
- não usar fallback numérico quando o BCB estiver indisponível.
