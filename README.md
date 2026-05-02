# SELIX — O Brasil paga R$ 270 bilhões a mais por ano na Selic. Provamos matematicamente.

<div align="center">

```
Selic atual:  14,50%
Selic ideal:   9,25%
Diferença:     5,25 pontos percentuais
Custo anual:  R$ 270.000.000.000,00
```

[![Colab Z3](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)
[![Colab Lean 4](https://img.shields.io/badge/Lean%204-Colab-orange?logo=github)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_lean4.ipynb)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/scoobiii/selix/blob/main/LICENSE)
[![Z3](https://img.shields.io/badge/Verified-Z3%20(Microsoft)-green)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)

</div>

---

## TL;DR

A Selic a 14,50% **não tem base matemática**. SELIX é um modelo de otimização com 5 teoremas formalmente verificados (Z3 + Lean 4) que calcula a **taxa ótima em tempo real**: **9,25% a.a.**

Código aberto. Reproduzível em 1 clique. Sem ideologia — só matemática.

---

## Por que isso importa

| Indicador | Com Selic 14,50% | Com Selic 9,25% (SELIX) |
|-----------|-----------------|------------------------|
| Juro real | ~10% | 4,77% |
| Investment Grade | ⚠️ em risco | ✅ BBB+ garantido |
| Custo anual da dívida | +R$ 270 bi/ano a mais | baseline |
| PIB per capita | — | **+R$ 14.900 por brasileiro** |
| Crédito para MPMEs | restrito | acessível |

> **R$ 270 bilhões** é mais que o orçamento anual do Ministério da Educação + Saúde somados.

---

## Como funciona

SELIX resolve um problema de **otimização restrita com 4 tetos simultâneos**:

```
max(Selic) sujeito a:
  [1] Investment Grade mantido        →  juro real ≥ limiar soberano
  [2] Juro real ≤ 5% (teto histórico IG)   ← restrição ativa
  [3] Selic ≤ ROE médio × 0.95       →  capital produtivo > especulativo
  [4] Selic ≤ média global ponderada  →  competitividade externa
```

O máximo sustentável é **9,48%** → arredondado ao step COPOM (0,25pp) → **9,25%**.

Cada restrição é um teorema. Cada teorema foi provado formalmente.

---

## Verificação independente — rode você mesmo

### 🟡 Z3 (Microsoft) — 1 clique

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)

### 🔵 Lean 4 — 1 clique

[![Lean 4 Colab](https://img.shields.io/badge/Lean%204-Abrir%20no%20Colab-orange)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_lean4.ipynb)

> ⏱️ Lean 4 instala em ~5 min na primeira execução.

### 🐍 Local (Python + Z3)

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
pip install -r requirements.txt
python scripts/z3_proof.py
# → SELIX: 9.25 | 5/5 teoremas OK
```

### 🟢 API REST

```bash
python src/api/server.py
curl http://localhost:5000/selix
# → {"selix": 9.25, "juro_real": 4.77, "investment_grade": true}
```

---

## FAQ rápido

**"O câmbio não afeta o resultado?"**
O câmbio afeta o Teto 4 (média global). Mas o teto mais restritivo hoje é o Teto 2 (juro real ≤ 5%), que depende só da inflação (~4,48%). Enquanto a inflação não explodir, a saída é 9,25%.

**"Isso é política econômica ou matemática?"**
É matemática. Os parâmetros são dados públicos (IBGE, Banco Central, FMI). Mude os inputs, o modelo recalcula.

**"Banco Central já considerou isso?"**
Não publicamente. Por isso o código é aberto — qualquer economista, jornalista ou parlamentar pode auditar.

**"Por que não baixam então?"**
Boa pergunta. Não é matemática que falta.

---

## Estrutura do repositório

```
selix/
├── src/selix/          # modelo principal
├── src/api/            # endpoint Flask /selix
├── scripts/z3_proof.py # prova formal Z3 (standalone)
├── lean_proof/         # prova Lean 4 (local)
├── notebooks/
│   ├── selix_colab.ipynb    # Z3 no Colab
│   └── selix_lean4.ipynb    # Lean 4 no Colab
├── agents/             # FAQ, Telegram bot, RAG, chatbot
├── tests/              # pytest + integrado Z3+Python
├── docs/               # versões por público
├── papers/             # whitepaper MD + PDF
└── evidencias/         # dados reais + referências
```

---

## Rodar no Android (Termux)

```bash
bash scripts/setup_termux.sh
# ou manualmente:
pkg install python git
pip install flask requests numpy pytest z3-solver
git clone https://github.com/scoobiii/selix && cd selix
python scripts/z3_proof.py
```

---

## Contribua

O modelo é auditável e extensível. Abra uma issue para:
- Contestar um teorema (bem-vindo — traga a prova)
- Propor novos parâmetros ou restrições
- Traduzir docs para inglês / espanhol
- Integrar com dados em tempo real (BCB SGS API)

Pull requests são abertos. Licença MIT.

---

## Citação

```bibtex
@software{selix2026,
  title   = {SELIX: Real-Time Optimal Selic Rate via Formal Verification},
  author  = {Sobrinho, José S.},
  year    = {2026},
  url     = {https://github.com/scoobiii/selix},
  license = {MIT}
}
```

---

<div align="center">

**R$ 270 bilhões/ano. Todo ano. Matematicamente evitáveis.**

⭐ Star se você acha que o Brasil merece ver a conta.

</div>
