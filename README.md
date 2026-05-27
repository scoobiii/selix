<div align="center">

# 🤖 SELIX — Sistema de Equilíbrio Linear de Juros e Investment Grade

**Selic atual:** 14,50% · **Selic ideal:** 9,48% · **Diferença:** 5,02 p.p. · **Custo anual:** R$ 341 bi

[![Colab Z3](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)
[![Lean 4](https://img.shields.io/badge/Lean%204-Proved-blue)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_lean4.ipynb)
[![Bluesky Bot](https://img.shields.io/badge/Bluesky-@selixbr-1DA1F2)](https://bsky.app/profile/selixbr.bsky.social)
[![TrampoForte](https://img.shields.io/badge/TrampoForte-Trabalhadores-28a745)](https://github.com/scoobiii/TrampoForte)

</div>

---

## 🎯 O que é a SELIX?

A **SELIX** (Sistema de Equilíbrio Linear de Juros e Investment Grade) é um modelo matemático que calcula a Taxa Selic ideal com base em **5 restrições formais**, provadas com Z3 (Microsoft Research) e Lean 4.

**Resultado principal:** SELIX = **9,48%** (Selic atual = 14,50%)

**Novo:** Agora também **defende os trabalhadores** via **TrampoForte** e **Bluesky Bot**!

---

## 📊 Por que isso importa

| Indicador | Com Selic 14,50% | Com SELIX 9,48% | Benefício |
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

## 🤖 Bluesky Bot (Novidade!)

**Publicação automática** defendendo trabalhadores no Bluesky: [@selixbr.bsky.social](https://bsky.app/profile/selixbr.bsky.social)

### Configurar e usar:

```bash
cd agents/bluesky_bot

# Configurar credenciais
cp .env.example .env
# Edite .env com sua senha do Bluesky

# Testar conexão
./scripts/manage.sh test

# Publicar manualmente
./scripts/manage.sh post 1  # Post geral
./scripts/manage.sh post 2  # Post curto
./scripts/manage.sh post 3  # Propositivo
./scripts/manage.sh post 4  # Com menções

# Iniciar bot automático
./scripts/manage.sh start

# Ver logs
tail -f logs/bot.log
```

Posts automáticos sobre:

· GPA/PLR: Trabalhadores sem PLR de R$2 mil
· Rentismo: Selic 14,5% > ROI do negócio
· Solução: SELIX (9,48%) + TrampoForte

---

👷 TrampoForte (Prioridade para Trabalhadores)

Lei que dá prioridade absoluta para: salários, PLR, FGTS e direitos trabalhistas em recuperação judicial.

🔗 github.com/scoobiii/TrampoForte

Impacto: Trabalhador recebe antes de bancos e rentistas!

---

📱 Conta Selic para diferentes plataformas

Desktop/Ubuntu

```bash
cd agents/conta_selic_ubuntu
python conta_selic_ubuntu.py
```

Mobile (Termux - Android)

```bash
cd agents/conta_selic_light
python conta_selic_termux.py
```

---

📊 Respostas Estratégicas (GPA/PLR)

Respostas prontas para 8 públicos-alvo:

```bash
agents/bluesky_bot/respostas_gpa_plr/
├── versao_bancos.txt        # Argumentos para bancos
├── versao_influencers.txt   # Para influenciadores
├── versao_justica.txt       # Para o Judiciário
├── versao_midia.txt         # Para imprensa
├── versao_poder.txt         # Para governo
├── versao_politicos.txt     # Para políticos
├── versao_sindicatos.txt    # Para sindicatos
└── versao_trabalhadores.txt # Para trabalhadores
```

---

🚀 Como executar

1. Google Colab (1 clique)

https://colab.research.google.com/assets/colab-badge.svg

2. Local (Python)

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Calcular SELIX
python src/selix/core.py

# Prova Z3
python scripts/z3_proof.py

# Preditor de energia
python src/energy/selix_predictor.py
```

3. API (servidor)

```bash
python src/api/server_v6.py
curl http://localhost:5000/selix
```

4. Docker

```bash
docker build -t selix .
docker run -p 5000:5000 selix
```

---

📁 Estrutura do repositório

```
selix/
├── src/
│   ├── selix/          # Modelo principal + prova Z3
│   ├── api/            # API Flask (/selix endpoint)
│   └── energy/         # SELIX Predictor
├── agents/
│   ├── bluesky_bot/    # 🤖 Bot do Bluesky (novo!)
│   ├── conta_selic_*   # 📱 Apps mobile/desktop
│   └── level_*         # Chatbots RAG/LLM
├── lean_proof/         # Prova Lean 4 completa
├── midias_sociais/     # Posts estratégicos
├── docs/               # Documentação por público
└── papers/             # Whitepapers
```

---

📈 Impacto acumulado (2000-2026)

Backtesting: O desvio da Selix custou ao Brasil:

· **R$ 5,8 trilhões** (R$ 2025)
· 49,6% do PIB de 2025
· 2,6 × o orçamento federal de 2025

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

🤝 Contribuições

Contribuições são bem-vindas! Áreas de interesse:

· ✅ Provar novos teoremas
· ✅ Melhorar o Bluesky Bot
· ✅ Expandir respostas estratégicas
· ✅ Adicionar novas plataformas

---

📄 Licença

MIT — Livre para usar, compartilhar e modificar.

---

🔗 Links importantes

Recurso Link
Repositório github.com/scoobiii/selix
Bluesky Bot @selixbr.bsky.social
TrampoForte github.com/scoobiii/TrampoForte
Whitepaper v4.1 PDF
Prova Lean 4 lean_proof/SELIX_v4_simple.lean
Colab notebooks/selix_colab.ipynb

---

<div align="center">

SELIX — Economia que prioriza quem trabalha! 🚀

</div>
