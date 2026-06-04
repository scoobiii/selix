
<div align="center">

# 🤖 SELIX v5.0 — Sistema de Inteligência Econômica Autônoma (Flex‑AI)

**Selic atual:** 14,50% · **Selic ideal:** 9,25% · **Economia anual:** R$ 270 bi

[![Colab Z3](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_colab.ipynb)
[![Lean 4](https://img.shields.io/badge/Lean%204-Proved-blue)](https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_lean4.ipynb)
[![Bluesky Bot](https://img.shields.io/badge/Bluesky-@zeh--sobrinho-1DA1F2)](https://bsky.app/profile/zeh-sobrinho.bsky.social)
[![API v5.0](https://img.shields.io/badge/API-v5.0-green)](https://github.com/scoobiii/selix)
[![Tests](https://img.shields.io/badge/tests-83%2F83-brightgreen)](https://github.com/scoobiii/selix)
[![Coverage](https://img.shields.io/badge/coverage-70%25-critical)](https://github.com/scoobiii/selix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🎯 O que é o SELIX?

O **SELIX** é um sistema econômico experimental que:

1. **Calcula a Taxa Selic ideal** usando 5 teoremas provados com Z3 (Microsoft Research) e Lean 4.
2. **Coleta dados reais** de mercado (Brent via Yahoo Finance, Selic via BCB) com **múltiplos provedores** e **zero fallback**.
3. **Publica automaticamente** no Bluesky, separando fatos de cenários, com **threads diárias**.
4. **Fornece API REST** (pública e administrativa) com proveniência de dados.
5. **É resiliente**: watchdog no Termux nativo reinicia serviços automaticamente após falhas.

**Resultado principal:** SELIX = **9,25%** (Selic atual = 14,50%)

---

## 📊 Para quem é o SELIX?

| Público | O que o SELIX oferece |
|---------|----------------------|
| **Trabalhadores** | Defesa da PLR, TrampoForte, threads no Bluesky |
| **Investidores** | Valuation de empresas em RJ (GPA +68%, Raízen +76%) |
| **Ambientalistas** | Mix energético E%/B%, emissões, solar, biogás |
| **Governo** | Economia de R$270 bi/ano, investment grade |
| **Desenvolvedores** | API REST, dados abertos, código versionado, testes 83/83 |

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

## 🤖 Bluesky Bot

O bot publica **3 posts por dia** (9h, 13h, 18h BRT) em thread, alternando entre diferentes segmentos (trabalhadores, investidores, governo, ambientalistas). O supervisor garante que as postagens ocorram mesmo após reinicializações.

**Perfil:** [@zeh-sobrinho.bsky.social](https://bsky.app/profile/zeh-sobrinho.bsky.social)

---

## 🛠️ Arquitetura e Resiliência

- **Worker multi‑provedor**: Yahoo Finance (Brent) + BCB (Selic) + cache de último valor real. Zero dados inventados.
- **Watchdog externo (Termux)**: monitora e reinicia worker, API, supervisor e metrics agent.
- **Recuperação automática**: serviços persistem mesmo após queda de energia (com Termux:Boot).
- **Testes**: 83 testes (administração, API, provedores, worker, segurança, métricas) – todos aprovados.

---

## 🚀 Instalação e uso (Termux / Linux)

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
./scripts/install.sh
bash start_selix.sh
```

Para executar apenas os testes:

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

---

📦 API REST

A API roda em http://localhost:5000. Endpoints principais:

Endpoint Método Descrição
/v1/health GET Status da API
/v1/selic GET Última Selic (real)
/v1/energia/mistura GET Brent e mix recomendado
/v1/empresas/rj GET Empresas listadas em RJ
/v1/admin/list_keys GET Lista chaves de API (admin)
/v1/admin/generate_key POST Gera nova chave (admin)

Chave mestra (admin) está no arquivo .env. Endpoints públicos não exigem chave.

---

📄 Licença

MIT © 2026 – Zeh Sobrinho, GOS3, MEX Energia

---

🔗 Links

· Repositório: https://github.com/scoobiii/selix
· Bluesky principal: @zeh-sobrinho.bsky.social
· Bluesky de monitoramento: @selixbr.bsky.social
· GitHub Pages: https://scoobiii.github.io/selix/

```
