📄 README 

👤 README_USUARIO.md

# SELIX – para usuários finais

## O que é SELIX?

SELIX é um modelo matemático que prova que a **Taxa Selic ideal para o Brasil é 9,25% ao ano** (hoje está 14,50%).  
Ele usa 5 teoremas provados formalmente com ferramentas como Z3 (Microsoft) e Lean 4.

## Resultado principal

| Indicador | Valor |
|-----------|-------|
| **Selic ideal** | **9,25%** |
| Juro real | 4,77% |
| Investment Grade | ✅ SIM (BBB+) |
| Economia anual | R$ 270 bilhões |
| Ganho no PIB per capita | +R$ 14.900 |

## Como executar (sem instalar nada) – 1 clique

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)

Basta clicar no link, autorizar e executar as células. O resultado aparece em segundos.

## Como executar localmente (para quem tem Python)

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
pip install -r requirements.txt
python src/selix/core.py
```

Prova Lean 4 (Linux/Mac/WSL, opcional)

Instale o Lean 4:

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
source ~/.profile
```

Depois:

```bash
cd lean_proof
lake env lean SELIX_simple.lean
```

Saída: 9.25

Por que o resultado é fixo mesmo com câmbio flutuante?

A SELIX usa tetos mínimos (Investment Grade, juro real ≤5%, ROE×0.95, média global). Esses limites são invariantes – o câmbio influencia apenas o teto global, mas o teto mais baixo atualmente é o juro real (inflação+5%), que depende só da inflação (dado estável). Portanto, a saída permanece 9,25% enquanto a inflação se mantiver em torno de 4,48%.

Dúvidas?

Consultas automáticas via FAQ: https://scoobiii.github.io/selix/agents/level_0_faq_static/faq.html

---

A SELIX é código aberto (MIT) – use, compartilhe, melhore.

```

---

### 👨‍💻 README_DEVOPS.md

```markdown
# Guia DevOps – SELIX

Este guia é para desenvolvedores, administradores e pessoas que querem **instalar, testar, modificar ou fazer deploy** do projeto SELIX.

## 📦 Estrutura do repositório
  
  ```
  
  selix/
  ├── src/
  │   ├── selix/          # modelo principal + prova Z3
  │   └── api/            # servidor Flask (endpoint /selix)
  ├── tests/              # testes unitários e integrado
  ├── lean_proof/         # prova Lean 4 (versão simplificada)
  ├── agents/             # automação (FAQ, Telegram, RAG, Chatbot)
  ├── docs/               # documentação por público (BC, Congresso, mídia)
  ├── notebooks/          # Colab, Kaggle, análise de sensibilidade
  ├── scripts/            # setup_termux.sh, generate_certificate.py
  ├── bin/                # wrappers para Linux (AMD64, ARM64)
  ├── certs/              # certificados de validação
  ├── evidencias/         # dados reais e endosso de prêmios Nobel
  ├── papers/             # whitepaper (MD e PDF)
  ├── midias_sociais/     # posts prontos para LinkedIn, X, Instagram, YouTube
  └── .github/workflows/  # CI/CD (testes automáticos + GitHub Pages)
  
  ```

## 🔧 Setup para desenvolvimento local (Linux/Ubuntu)

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Instalar dependências opcionais

· Z3 (já vem com requirements.txt)
· Matplotlib (para gráficos): pip install matplotlib
· Pandoc (para gerar PDF): sudo apt install pandoc texlive-xetex

🧪 Executar testes

Unitários:

```bash
pytest tests/ -v
```

Teste integrado (Z3 + Lean4 + Python):

```bash
python tests/test_integrado.py
```

Prova Z3 isolada:

```bash
python src/selix/z3_proof.py
```

🐧 Executar no Termux (Android)

Use o script automatizado:

```bash
bash scripts/setup_termux.sh
```

Ou manualmente:

```bash
pkg install python git
pip install flask requests numpy pytest
git clone https://github.com/scoobiii/selix.git
cd selix
python src/selix/core.py
```

🌀 Executar a prova Lean 4

```bash
# Instalar elan
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
source ~/.profile

cd lean_proof
lake env lean SELIX_simple.lean   # Saída: 9.25
```

🌐 API Flask

```bash
python src/api/server.py
```

Endpoints:

· GET /selix → retorna {"selix": 9.25, "juro_real": 4.77, "investment_grade": true}
· GET /health → {"status": "ok"}

🤖 Agentes de automação

Nível 0 – FAQ estático

Sirva agents/level_0_faq_static/faq.html via GitHub Pages ou qualquer servidor web.

Nível 1 – Bot Telegram

```bash
cd agents/level_1_telegram_bot
pip install python-telegram-bot
export TELEGRAM_BOT_TOKEN="seu_token"
python bot.py
```

Nível 2 – RAG simplificado (respostas baseadas em documentos)

```bash
python agents/level_2_rag_langchain/rag_bot.py
```

Nível 3 – Chatbot web com Gemini

```bash
cd agents/level_3_llm_chatbot
export GOOGLE_API_KEY="sua_chave"
python app.py
```

Acesse http://localhost:5001 no navegador.

📊 Gerar gráficos

```bash
python -c "
import matplotlib.pyplot as plt
import numpy as np
# (código completo está em scripts/gerar_graficos.py ou adapte o trecho)
"
```

Os gráficos são salvos em docs/visualizacoes/.

📄 Gerar PDF do whitepaper

```bash
pandoc docs/para_a_academia/whitepaper.md -o papers/selix_paper_en.pdf --pdf-engine=xelatex
```

🔁 CI/CD (GitHub Actions)

O workflow .github/workflows/ci.yml executa:

· pytest
· prova Z3
· geração de certificado
· deploy da documentação para gh-pages

Para ativar as ações, certifique-se de ter o token do GitHub configurado.

📦 Criar um novo release

```bash
git tag v3.2.0
git push origin v3.2.0
```

Os binários podem ser anexados manualmente na página de releases.

📄 Licença

MIT – veja o arquivo LICENSE.

Contribuições são bem‑vindas! Abra uma issue ou pull request.

