
## SELIX — Sistema de Equilíbrio Linear de Juros e Investment Grade

<div align="center">

```

Selic atual:  14,50%
Selic ideal:   9,48%
Diferença:     5,02 pontos percentuais
Custo anual:  R$ 341 bilhões

```

[![Colab Z3](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)
[![Lean 4](https://img.shields.io/badge/Lean%204-Proved-blue)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_lean4.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Z3](https://img.shields.io/badge/Verified-Z3%20(Microsoft)-green)](scripts/z3_proof.py)

</div>

---

## 🎯 O que é a SELIX?

A **SELIX** (Sistema de Equilíbrio Linear de Juros e Investment Grade) é um modelo matemático que calcula a Taxa Selic ideal com base em **5 restrições formais**, provadas com Z3 (Microsoft Research) e Lean 4.

**Resultado principal:** SELIX = **9,48%** (Selic atual = 14,50%)

---

## 📊 Por que isso importa

| Indicador | Com Selic 14,50% | Com SELIX 9,48% | Benefício |
|-----------|-----------------|-----------------|-----------|
| Juro real | 10,02% | 4,77% | -5,25 p.p. |
| Investment Grade | ❌ BB | ✅ BBB+ | +2 níveis |
| Custo anual da dívida | R$ 650 bi | R$ 380 bi | **Economia de R$ 270 bi/ano** |
| PIB per capita | R$ 59.600 | R$ 60.394 | **+R$ 794 por brasileiro** |
| Convergência | — | 10,5 meses | Cortes de 0,5%/mês |

---

## 🔬 Os 5 Teoremas Provados

| Teorema | Enunciado | Status |
|---------|-----------|--------|
| **T1** | SELIX ≤ 9,99% (Investment Grade) | ✅ Z3 + Lean 4 |
| **T2** | SELIX ≤ ROE × 0,95 (Não canibaliza) | ✅ Z3 + Lean 4 |
| **T3** | SELIX - inflação ≤ 5% (Juro real máximo) | ✅ Z3 + Lean 4 |
| **T4** | 14,50% > SELIX (Convergência possível) | ✅ Z3 + Lean 4 |
| **T5** | Sistema é consistente (existe solução) | ✅ Z3 + Lean 4 |

---

## 🚀 Como executar

### Google Colab (1 clique)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)

### Local (Python)
```bash
git clone https://github.com/scoobiii/selix.git
cd selix
pip install -r requirements.txt
python src/selix/core.py
```

Prova Lean 4 (Colab)

https://img.shields.io/badge/Lean%204-Proved-blue

Prova Z3

```bash
python src/selix/z3_proof.py
```

SELIX Energy (Predictor)

```bash
python src/energy/selix_predictor.py
```

---

📁 Estrutura do repositório

```
selix/
├── src/
│   ├── selix/          # Modelo principal + prova Z3
│   ├── api/            # API Flask (/selix endpoint)
│   └── energy/         # SELIX Predictor (previsão de preços)
├── lean_proof/         # Prova Lean 4 completa
├── tests/              # Testes unitários + integrado
├── notebooks/          # Colab, Kaggle, Lean 4
├── docs/               # Documentação por público
├── papers/             # Whitepaper v4.0 e v4.1
├── agents/             # Bots (Telegram, RAG, Chatbot)
└── midias_sociais/     # Posts para redes sociais
```

---

📈 Impacto acumulado (2000-2026)

Backtesting histórico mostra que o desvio da Selix custou ao Brasil:

· Custo acumulado: R$ 5,8 trilhões (R$ 2025)
· Equivalente a 49,6% do PIB de 2025
· Ou 2,6 × o orçamento federal de 2025

---

⚡ SELIX Predictor (Ferramenta em Tempo Real)

O SELIX Predictor captura indicadores de mercado em tempo real e recomenda a mistura ideal de etanol (E27/E30/E35/E40/E42) com base no preço do Brent e no risco geopolítico (GPR).

Última execução (03/05/2026):

· Brent spot: US$ 108.17
· Risco geopolítico: 85/100 (ALERTA)
· Recomendação: E40 em 24h

```bash
python src/energy/selix_predictor.py
```

---

📄 Whitepapers

Versão Conteúdo Link
v4.1 Juros + Energia + Raízen PDF
v4.0 Juros + Energia (crise 2026) MD

---

👥 Autores

· Zeh Sobrinho — Criador do modelo
· GOS3 — Grupo de Otimização de Sistemas Econômicos

---

📄 Licença

MIT — Livre para usar, compartilhar e modificar.

---

🔗 Links

· Repositório: https://github.com/scoobiii/selix
· Whitepaper v4.1 (PDF): https://github.com/scoobiii/selix/blob/main/papers/SELIX_v4.1_PT_COMPLETO.pdf
· Prova Lean 4: https://github.com/scoobiii/selix/blob/main/lean_proof/SELIX_v4_simple.lean
· Colab (modelo): https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb
· SELIX Predictor: https://github.com/scoobiii/selix/blob/main/src/energy/selix_predictor.py

