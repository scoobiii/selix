# Limitações do SELIX — v7.2

Este documento lista de forma transparente o que o SELIX **não faz**, **não prova** e **não substitui**.

---

## 1. Não é um modelo DSGE/SAMBA

O SELIX não é um modelo de equilíbrio geral dinâmico e estocástico. Não substitui o **SAMBA do BCB** nem qualquer modelo de política monetária completo.

**O que faz:** auditoria aritmética da consistência entre parâmetros macro e a Selic atual.

**O que não faz:** prever inflação, PIB, câmbio ou qualquer variável endógena.

---

## 2. Credibilidade ainda é hardcoded

O parâmetro `credibilidade` no `core.py` está fixado em **0,50** (50%). Não há derivação endógena a partir de dados históricos do BCB (Focus vs realizado).

**Impacto:** a Selic ideal é sensível a esse parâmetro. Com credibilidade 0,70, o juro real necessário cai ~0,8 p.p.; com 0,30, sobe ~1,0 p.p.

**Próximo passo:** v7.3 deve tornar a credibilidade endógena (função `get_credibilidade_from_focus()` baseada em dados reais).

---

## 3. Gap de produto é fixo

O `gap_produto` no baseline atual é **+0,50%** (dado do BCB RPM 2º tri/2026). Mas o código não puxa esse dado automaticamente da API do BCB.

**Impacto:** se o gap mudar de sinal ou magnitude, a Selic ideal varia em ±0,25 p.p. por 0,5 p.p. de gap.

**Próximo passo:** integrar `gap_produto` dinâmico via `focus_api.py` ou API do BCB.

---

## 4. Mistura energética (E32/B15) é fixa

O fator `τ` (blindagem energética) é calculado com base nos valores fixos `etanol_gasolina=32.0` e `biodiesel_diesel=15.0`. Não é puxado da ANP em tempo real.

**Impacto:** a vantagem do Brasil (biocombustíveis) é capturada, mas com dados estáticos.

**Próximo passo:** integrar com a API da ANP ou com o endpoint `/v1/energia/mistura` existente.

---

## 5. Conversão real → nominal não é explícita

O resultado da fórmula (`juro_real_necessario`) é chamado de "Selic ideal" no código e no dashboard. Tecnicamente, juro real e Selic nominal são diferentes. Falta a equação de Fisher:

```

Selic_nominal ≈ juro_real + inflação_esperada

```

**Impacto:** a Selic ideal publicada (7,00%) pode ser subestimada em relação a uma regra de Taylor convencional (~11%).

**Próximo passo:** adicionar a conversão real → nominal no `core.py` e no dashboard.

---

## 6. Provas Lean/Z3 são de consistência, não de otimidade

Os teoremas T7–T11 no `lean_proof/` provam que a fórmula escolhida **é consistente** com os inputs e que o valor quantizado ao grid do Copom está correto.

**O que não provam:** que essa fórmula é a "ótima" do ponto de vista de bem-estar social ou que a Selic atual deveria ser 7,00%.

**Uso recomendado:** auditoria aritmética, não substituição de decisão de política monetária.

---

## 7. Integrações com APIs são placeholders parciais

- `focus_api.py`: usa `requests.get` com timeout, mas ainda não está integrado ao `BASELINE_ATUAL`.
- `roic_cvm.py`: depende de pandas e requests, mas o download do ITR da CVM ainda não está testado em produção.
- `embi_api.py` e `commodities.py` são placeholders para dados reais.

**Próximo passo:** tornar todos os parâmetros dinâmicos via APIs reais.

---

## Conclusão

O SELIX é uma ferramenta de **auditoria aritmética e transparência**, não um modelo de política monetária completo. Seu valor está na **reprodutibilidade**, **código aberto** e **formalização explícita** dos parâmetros e da fórmula.

Ele **não substitui** o COPOM, o BCB ou qualquer modelo DSGE. Mas ajuda a responder: *"Se eu usar esses parâmetros, o que a Selic deveria ser?"* — com a ressalva de que os parâmetros são escolhas do usuário, e não verdades universais.

---

*Última atualização: 05/ago/2026 — v7.2*
