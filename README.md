<div align="center">

# 🤖 SELIX — Sistema de Equilíbrio Linear de Juros e Investment Grade

**Selic atual:** 14,50% · **Selic ideal:** 9,25% · **Diferença:** 5,25 p.p. · **Economia anual:** R$ 270 bi

[![Colab Z3](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)
[![Lean 4](https://img.shields.io/badge/Lean%204-Proved-blue)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_lean4.ipynb)
[![Bluesky Bot](https://img.shields.io/badge/Bluesky-@selixbr-1DA1F2)](https://bsky.app/profile/selixbr.bsky.social)
[![API v3.0](https://img.shields.io/badge/API-v3.0-green)](https://github.com/scoobiii/selix)

</div>

---

## 🎯 O que é a SELIX?

A **SELIX** (Sistema de Equilíbrio Linear de Juros e Investment Grade) é um modelo matemático que calcula a Taxa Selic ideal com base em **5 restrições formais**, provadas com Z3 (Microsoft Research) e Lean 4.

**Resultado principal:** SELIX = **9,25%** (Selic atual = 14,50%)

**Novo:** Agora também **defende os trabalhadores** via **TrampoForte**, **Bluesky Bot** e **Energy Predictor** (mistura de etanol e biodiesel em tempo real).

---

## 📊 Por que isso importa

| Indicador | Com Selic 14,50% | Com SELIX 9,25% | Benefício |
|-----------|-----------------|-----------------|-----------|
| Juro real | 10,02% | 4,77% | -5,25 p.p. |
| Investment Grade | ❌ BB | ✅ BBB+ | +2 níveis |
| Custo anual da dívida | R$ 650 bi | R$ 380 bi | **Economia de R$ 270 bi/ano** |
| PIB per capita | R$ 59.600 | R$ 60.394 | **+R$ 794 por brasileiro** |

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

## ⚡ Energy Predictor – API v3.0

A API REST em tempo real calcula a **mistura ideal de etanol (E%) e biodiesel (B%)** com base no preço do petróleo Brent, além de fornecer dados sobre termelétricas flexíveis, commodities e empresas em recuperação judicial.

### Endpoints disponíveis

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/v1/health` | Health check da API |
| `GET` | `/v1/energia/mistura` | Recomendação E% e B% com Brent atual |
| `GET` | `/v1/energia/mistura/<brent>` | Simulação para valor específico de Brent |
| `GET` | `/v1/energia/termicas` | Lista de termelétricas flexíveis (capacidade) |
| `GET` | `/v1/energia/gatilhos` | Tabela de gatilhos de mistura (E%, B%) |
| `GET` | `/v1/commodities` | Preços atualizados de commodities (Brent, etc.) |
| `GET` | `/v1/empresas/rj` | Empresas em recuperação judicial com valuation SELIX |

### Exemplo de resposta (`/v1/energia/mistura`)

```json
{
  "brent_usd": 87.36,
  "etanol": {
    "mistura": "E30",
    "status": "ALERTA",
    "tempo": "72h",
    "cor": "🟡"
  },
  "biodiesel": {
    "mistura": "B15",
    "status": "ALERTA",
    "tempo": "48h",
    "cor": "🟡"
  },
  "termicas": 12750,
  "data": "2026-05-30T19:23:59"
}
```

---

🚀 Como executar (instalação completa)

1. Google Colab (1 clique – para testes rápidos)

https://colab.research.google.com/assets/colab-badge.svg

2. Local (Python – produção)

```bash
# Clone o repositório
git clone https://github.com/scoobiii/selix.git
cd selix

# Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instale as dependências
pip install -r requirements.txt

# Calcular SELIX (modelo principal)
python src/selix/core.py

# Executar prova Z3 (5 teoremas)
python scripts/z3_proof.py

# Iniciar a API v3.0 (Energy Predictor)
python src/api/main_v3.py
```

3. Usar a API (em outro terminal)

```bash
# Health check
curl http://localhost:5000/v1/health

# Mistura atual
curl http://localhost:5000/v1/energia/mistura

# Simular Brent a US$ 150
curl http://localhost:5000/v1/energia/mistura/150

# Listar termelétricas
curl http://localhost:5000/v1/energia/termicas

# Ver gatilhos de mistura
curl http://localhost:5000/v1/energia/gatilhos

# Commodities
curl http://localhost:5000/v1/commodities

# Empresas em RJ
curl http://localhost:5000/v1/empresas/rj
```

4. Docker (opcional)

```bash
docker build -t selix .
docker run -p 5000:5000 selix
```

---

🤖 Bluesky Bot

Publicação automática defendendo trabalhadores: @selixbr.bsky.social

Configurar e usar

```bash
cd agents/bluesky_bot

# Configure suas credenciais
cp .env.example .env
nano .env   # preencha BLUESKY_USERNAME e BLUESKY_PASSWORD (app password)

# Testar conexão
python -c "from core.bluesky_client import BlueskyClient; print(BlueskyClient().authenticate())"

# Publicar um post de teste
python post_final_corrigido.py
```

Nota: Para automação completa, use o agendador em agents/monitor/scheduler_fixo.py ou configure um cron job.

---

👷 TrampoForte – Prioridade para Trabalhadores

Lei que dá prioridade absoluta para salários, PLR, FGTS e direitos trabalhistas em recuperação judicial.

🔗 github.com/scoobiii/TrampoForte

Impacto: Trabalhador recebe antes de bancos e rentistas.

---

📁 Estrutura do repositório (v3.0)

```
selix/
├── src/
│   ├── selix/
│   │   ├── core.py            # Modelo principal (Selic 9,25%)
│   │   ├── energy_predictor.py# Lógica do Energy Predictor
│   │   ├── database.py        # SQLite (worker + histórico)
│   │   └── worker.py          # Coleta periódica de commodities
│   ├── api/
│   │   └── main_v3.py         # API REST (endpoints /v1/*)
│   └── energy/                # (legado, mantenha compatibilidade)
├── agents/
│   ├── bluesky_bot/           # Bot do Bluesky + threads
│   ├── conta_selic_*          # Apps mobile/desktop
│   └── level_*                # Chatbots RAG/LLM
├── lean_proof/                # Prova Lean 4 (SELIX_simple.lean)
├── scripts/                   # Utilitários (z3_proof.py, etc.)
├── tests/                     # Testes unitários
├── docs/                      # Documentação por público-alvo
├── papers/                    # Whitepapers
└── notebooks/                 # Colab, análise de sensibilidade
```

---

📈 Impacto acumulado (2000-2026)

Backtesting: o desvio da Selix custou ao Brasil:

· R$ 5,8 trilhões (valores de 2025)
· 49,6% do PIB de 2025
· 2,6 × o orçamento federal de 2025

---

📄 Whitepapers

Versão Conteúdo Link
v4.1 Juros + Energia + Raízen PDF
v4.0 Juros + Energia (crise 2026) MD

---

👥 Autores

· Zeh Sobrinho – Criador do modelo
· GOS3 – Grupo de Otimização de Sistemas Econômicos

---

🤝 Contribuições

Contribuições são bem-vindas! Áreas de interesse:

· ✅ Provar novos teoremas
· ✅ Melhorar o Energy Predictor
· ✅ Integrar o Bluesky Bot com a API v3.0
· ✅ Adicionar novos endpoints (alertas, previsões)

---

📄 Licença

MIT – Livre para usar, compartilhar e modificar.

---

🔗 Links importantes

Recurso Link
Repositório github.com/scoobiii/selix
Bluesky Bot @selixbr.bsky.social
TrampoForte github.com/scoobiii/TrampoForte
Whitepaper v4.1 PDF
Prova Lean 4 lean_proof/SELIX_simple.lean
Colab notebooks/selix_colab.ipynb

---

<div align="center">

SELIX — Economia que prioriza quem trabalha! 🚀

</div>

