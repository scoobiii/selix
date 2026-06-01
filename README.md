<div align="center">

# 🤖 SELIX v4.0 — Sistema de Equilíbrio Linear de Juros e Investment Grade

**Selic atual:** 14,50% · **Selic ideal:** 9,25% · **Economia anual:** R$ 270 bi

[![Colab Z3](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)
[![Lean 4](https://img.shields.io/badge/Lean%204-Proved-blue)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_lean4.ipynb)
[![Bluesky Bot](https://img.shields.io/badge/Bluesky-@zeh--sobrinho-1DA1F2)](https://bsky.app/profile/zeh-sobrinho.bsky.social)
[![API v4.0](https://img.shields.io/badge/API-v4.0-green)](https://github.com/scoobiii/selix)
[![Tests](https://img.shields.io/badge/tests-15%2F15-brightgreen)](https://github.com/scoobiii/selix)
[![Coverage](https://img.shields.io/badge/coverage-41%25-yellow)](https://github.com/scoobiii/selix)

</div>

---

## 🎯 O que é o SELIX?

O **SELIX** é um sistema econômico experimental que:

1. **Calcula a Taxa Selic ideal** usando 5 teoremas provados com Z3 (Microsoft Research) e Lean 4
2. **Coleta dados reais** de mercado (Brent, Selic, combustíveis, gás natural)
3. **Publica automaticamente** no Bluesky, separando **fatos** de **cenários**
4. **Fornece API REST** com proveniência de dados (rastreabilidade)

**Resultado principal:** SELIX = **9,25%** (Selic atual = 14,50%)

---

## 📊 Para quem é o SELIX?

| Público | O que o SELIX oferece |
|---------|----------------------|
| **Trabalhadores** | Defesa da PLR, TrampoForte, threads no Bluesky |
| **Investidores** | Valuation de empresas em RJ (GPA +68%, Raízen +76%) |
| **Ambientalistas** | Mix energético E%/B%, emissões, solar, biogás |
| **Governo** | Economia de R$270 bi/ano, investment grade |
| **Desenvolvedores** | API REST, dados abertos, código versionado |

---

## 🔬 Os 5 Teoremas Provados

| Teorema | Enunciado | Status |
|---------|-----------|--------|
| **T1** | SELIX ≤ 9,99% (Investment Grade) | ✅ Z3 + Lean 4 |
| **T2** | SELIX ≤ ROE × 0,95 | ✅ Z3 + Lean 4 |
| **T3** | SELIX - inflação ≤ 5% | ✅ Z3 + Lean 4 |
| **T4** | 14,50% > SELIX | ✅ Z3 + Lean 4 |
| **T5** | Sistema é consistente | ✅ Z3 + Lean 4 |

---

## 🚀 Como executar (usuário final)

### Opção 1 — Google Colab (1 clique)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)

### Opção 2 — Local (Python)

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Calcular Selic ideal
python src/selix/core.py

# Iniciar API
python src/api/main_v4.py
```

### Opção 3 — Docker

```bash
docker build -t selix .
docker run -p 5000:5000 selix
```

---

## 🤖 Bluesky Bot

O bot publica threads diárias separando fatos (dados reais) de cenários (projeções).

**Perfil:** [@zeh-sobrinho.bsky.social](https://bsky.app/profile/zeh-sobrinho.bsky.social)

**Exemplo de post:**
```
📊 Dados observados
Brent: US$97.36 (fonte: OilPriceAPI)
github.com/scoobiii/selix

🎯 Cenário Selix_925 (Selic 9,25%)
PIB per capita: US$130,000
B3 Market Cap: US$10,000,000,000,000
```

---

## 📡 API Endpoints (v4.0)

| Endpoint | Descrição |
|----------|-----------|
| `GET /v1/health` | Status da API |
| `GET /v1/energia/mistura` | Mix E/B com Brent atual |
| `GET /v1/energia/mistura/<brent>` | Simulação para Brent específico |
| `GET /v1/energia/termicas` | Lista usinas termelétricas |
| `GET /v1/energia/gatilhos` | Gatilhos de mistura |
| `GET /v1/commodities` | Histórico de commodities |
| `GET /v1/empresas/rj` | Empresas em RJ com valuation |
| `GET /v1/selic` | Selic histórica |
| `GET /v1/precos/energeticos` | Preços gasolina, diesel, etanol |
| `GET /v1/sentimento` | Sentimento de mercado |
| `GET /v1/alertas/geral` | Alertas automáticos |
| `GET /v1/faq` | Perguntas frequentes |

---

## 📊 Dados em Tempo Real

| Indicador | Valor | Fonte |
|-----------|-------|-------|
| Brent | ~US$97 | OilPriceAPI |
| Selic | 14,25% | BCB |
| TTF (Europa) | ~€49 / MWh | Yahoo Finance |
| Rating Brasil | AA | Selix (modelo) |

---

## 👥 Autores e Licença

- **Zeh Sobrinho** — Criador do modelo
- **GOS3** — Grupo de Otimização de Sistemas Econômicos

**Licença:** MIT — livre para usar, compartilhar e modificar.

---

## 🔗 Links

| Recurso | Link |
|---------|------|
| Repositório | [github.com/scoobiii/selix](https://github.com/scoobiii/selix) |
| Bluesky Bot | [@zeh-sobrinho.bsky.social](https://bsky.app/profile/zeh-sobrinho.bsky.social) |
| Whitepaper | `papers/selix_paper_v4.0.pdf` |
| Prova Lean 4 | `lean_proof/SELIX_simple.lean` |

---

<div align="center">

**SELIX — Economia que prioriza quem trabalha 🚀**

</div>
