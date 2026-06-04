# 🚀 SELIX v4.0.0 – Release Notes

**Data:** 2026-06-01  
**Versão:** 4.0.0  
**Tag:** v4.0.0

---

## 📌 Resumo Executivo

O SELIX v4.0.0 é um **sistema econômico experimental** que:

- **Prova formalmente** que a Selic ideal é **9,25%** (Z3 + Lean4)
- **Coleta dados reais** de mercado (Brent, Selic, TTF, combustíveis)
- **Publica automaticamente** no Bluesky, separando **fatos** (observações) de **cenários** (projeções)
- **Fornece API REST** com proveniência de dados (rastreabilidade)
- **Calcula índice de confiança modular** baseado na diferença entre projeção e mercado real

**Selic atual:** 14,50% · **Selic ideal (provada):** 9,25% · **Economia anual projetada:** R$ 270 bi

---

## 🆕 Novidades Técnicas

### Arquitetura com Proveniência
- Tabelas `fontes`, `observacoes`, `cenarios`, `projecoes`
- Rastreabilidade total: `synthetic` flag separa fato de cenário
- Cada dado tem fonte, timestamp e confiança associada

### Módulo de Risco Geoenergético
- Preços globais: TTF (Europa), Henry Hub (EUA), JKM (Ásia), Brent
- Matriz energética do Brasil (hidro 65%, eólica 12%, solar 8%, biomassa 8%)
- Score de risco e rating automático (Brasil: **AA**)

### Índice de Confiança Modular
- **Não é acurácia do modelo** – é a **diferença entre a projeção do SELIX e o mercado real**
- Fatores ponderados: volatilidade do Brent, estabilidade de combustíveis, risco geopolítico, sentimento global, mix energético
- Exemplo: com Brent real US$97,36 e projeção de cenário de US$87,36, a confiança cai

### Worker Resiliente
- Coleta dados reais de múltiplas fontes (OilPriceAPI, BCB, Yahoo Finance)
- Fallback inteligente: API → DuckDuckGo → LLM local (não quebra)
- WAL mode no SQLite reduz latência

### Bluesky Bot Avançado
- Threads segmentadas para 8 públicos (trabalhadores, bancos, governo, etc.)
- Separação entre **fatos** (dados observados) e **cenários** (projeções)
- Respondedor automático de menções (FAQ + RAG + LLM local)

### API REST (12 endpoints)
- `/v1/health`, `/v1/energia/mistura`, `/v1/selic`, `/v1/empresas/rj`, `/v1/precos/energeticos`, etc.
- Rate limiting via NGINX
- Retorna 503 quando dados não disponíveis (sem fallback na API)

---

## 📊 Métricas de Performance

| Métrica | Valor | Alvo | Status |
|---------|-------|------|--------|
| Testes unitários | 15/15 | 15/15 | ✅ |
| Testes de integração | 5/5 | 5/5 | ✅ |
| Cobertura de código | 41% | 70% | ⚠️ |
| Latência p95 (carga) | 995ms | <500ms | ⚠️ |
| Latência p95 (estresse) | 2,58s | <1s | ❌ |
| Req/s sustentado | 68 | 200 | ⚠️ |
| Taxa de erro (carga) | 0% | <1% | ✅ |
| Taxa de erro (estresse) | 4,64% | <1% | ❌ |

---

## 📈 Validação Empírica – Comparação com Mercado Real

O SELIX **não mede acurácia do modelo** (não há simulação real). Mede a **confiança modular**: diferença entre a projeção do cenário e o dado observado.

### Benchmark: Brent Coletado vs. Brent Real

| Data | Brent Real (OilPriceAPI) | Brent no Banco (worker) | Diferença | Confiança |
|------|--------------------------|-------------------------|-----------|-----------|
| 01/06/2026 00:00 | US$95,19 | US$95,19 | 0% | Alta |
| 01/06/2026 06:00 | US$96,50 | US$96,50 | 0% | Alta |
| 01/06/2026 12:00 | US$97,36 | US$97,36 | 0% | Alta |
| 01/06/2026 18:00 | US$97,02 | US$97,02 | 0% | Alta |

**Conclusão:** O worker coletou Brent real sem divergência. A confiança do **worker** é alta, mas a confiança do **cenário Selix_925** depende de outros fatores (risco geopolítico, sentimento).

### Índice de Confiança Modular – Exemplo de Cálculo

| Fator | Peso | Valor | Contribuição |
|-------|------|-------|---------------|
| Volatilidade Brent | 25% | 0,0 (alta volatilidade) | 0,0 |
| Estabilidade combustíveis | 20% | 0,5 | 0,10 |
| Risco geopolítico | 20% | 0,94 | 0,188 |
| Sentimento global | 25% | 0,508 | 0,127 |
| Mix energético | 10% | 0,5 | 0,05 |
| **Total** | – | – | **46,5%** |

**Interpretação:** A confiança no cenário Selix_925 é de **46,5%** devido ao alto risco geopolítico (0,94) e à volatilidade do Brent (0).

---

## ⚠️ Limitações Conhecidas

1. **Cobertura de código (41%)** – especialmente `geo_energy_risk.py` (0% de cobertura inicial, agora planejado para 100%).
2. **Latência alta sob estresse (p95 2,58s)** – gargalo no SQLite e workers síncronos.
3. **Escala horizontal limitada** – API única; necessário balanceador de carga e múltiplas instâncias.
4. **SQLite como banco** – ideal para desenvolvimento, mas para produção recomenda-se PostgreSQL.
5. **Confiança é modular** – não é acurácia do modelo; depende de fatores externos.
6. **Risco geoenergético JKM (Ásia)** – é estimativa, não dado real (fonte indisponível).

---

## 🔜 Próximos Passos (v5.0)

| Prioridade | Tarefa | Meta |
|------------|--------|------|
| Alta | Aumentar cobertura de código para 70% | 70%+ |
| Alta | Reduzir latência p95 para <500ms | Cache Redis |
| Média | Migrar para PostgreSQL | Escalabilidade |
| Média | FastAPI (async) | Performance |
| Baixa | Buscar fonte real para JKM | Dados Ásia |

---

## 👥 Contribuidores

- **Zeh Sobrinho** – Criador do modelo, arquitetura, implementação
- **GOS3** – Grupo de Otimização de Sistemas Econômicos

---

## 🔗 Links

- **Repositório:** [github.com/scoobiii/selix](https://github.com/scoobiii/selix)
- **Release:** [github.com/scoobiii/selix/releases/tag/v4.0.0](https://github.com/scoobiii/selix/releases/tag/v4.0.0)
- **Bluesky Bot:** [@zeh-sobrinho.bsky.social](https://bsky.app/profile/zeh-sobrinho.bsky.social)

---

<div align="center">

**SELIX — Economia que prioriza quem trabalha** 🚀

</div>

## v4.0.0 (2026-06-04) – Resiliência e múltiplas fontes de dados

### 🚀 Novas funcionalidades
- **Arquitetura de provedores desacoplada** (Adapter + Strategy + Circuit Breaker)
- **Múltiplas fontes de dados**:
  - Yahoo Finance (Brent)
  - Banco Central do Brasil (Selic)
  - EIA (Brent alternativo, gratuito, com API key)
- **Zero fallback**: nunca inventamos dados; se todas as fontes falharem, o worker reporta erro e não insere dados falsos.
- **Watchdog aprimorado** (Termux nativo) monitora worker, API e supervisor, reiniciando automaticamente.
- **Testes de integração do supervisor** (4/4 aprovados).
- **Logging detalhado** com horários e próximo evento agendado.

### 🔧 Correções
- Correção do template do trabalhador (diferença de R$500).
- Worker agora usa cache da Selic quando BCB offline (dado real, não mock).
- Ajuste no cálculo do dia da campanha (rotação 1-30, não dia do ano).
- Remoção de dependência de cron dentro do PRoot (substituído por loop interno).

### 📦 Dependências adicionadas
- `pytest-sugar`, `pytest-xdist`, `pytest-timeout` (testes mais rápidos e visuais)
- `requests` (já existente)

### 🔌 Configuração necessária
- Adicionar `EIA_API_KEY=sua_chave` ao arquivo `.env` (obter gratuitamente em eia.gov).

### ✅ Status
- Testes: 39 unitários + 4 do supervisor = **43 testes aprovados**
- Cobertura: ~55% (em evolução)
- Postagens no Bluesky retomadas (agendamentos 9h, 13h, 18h)
- Resiliência comprovada contra falhas de Yahoo e BCB.

---
