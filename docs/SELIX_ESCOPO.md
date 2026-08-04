# 📋 SELIX — Escopo, Limitações e Roadmap

## 🟢 O que o SELIX É

| Item | Descrição | Status |
|------|-----------|--------|
| **Ferramenta de auditoria aritmética** | Prova formal no Lean/Z3 de consistência entre parâmetros e resultado | ✅ 100% |
| **API REST** | Endpoints públicos/privados com autenticação | ✅ 100% |
| **Bot Bluesky** | Postagens automáticas sobre economia | ✅ 100% |
| **Mobile-first** | Roda 24/7 no Termux/Android | ✅ 100% |
| **Dados em tempo real** | BCB (Selic), Yahoo Finance (Brent) | ✅ 100% |
| **Transparência** | Código aberto, dados públicos, rastreável | ✅ 100% |
| **Modelo regime-dependente** | juro_real = inflação × (1 + prêmio_risco) × (1 + (1 - credibilidade) × 0.5) | ✅ 100% |
| **93/93 testes** | Cobertura total do core | ✅ 100% |
| **Provas formais T7, T8, T9, T11** | Lean/Z3 com dados históricos | ✅ 100% |

---

## 🔴 O que o SELIX NÃO É

| Item | Descrição | Motivo |
|------|-----------|--------|
| **Modelo DSGE** | Não é um modelo de equilíbrio geral dinâmico e estocástico (SAMBA do BCB) | Fora do escopo — requer infraestrutura computacional pesada |
| **Accountability institucional** | Não tem mandato legal nem acesso a dados internos do sistema financeiro | Não é uma instituição pública |
| **Previsão estocástica** | Não incorpora incerteza com simulações de Monte Carlo | O foco é auditoria, não previsão |
| **Derivação endógena completa** | prêmio_risco, credibilidade, choques (oil/TTF) ainda são inputs | Será resolvido no v7.0 |
| **Substituto do COPOM** | Não substitui a decisão do Comitê de Política Monetária | O COPOM considera fatores qualitativos não modelados |

---

## 🟡 O que o SELIX VAI SER (Roadmap v7.0)

| Item | Descrição | Status | Previsão |
|------|-----------|--------|----------|
| **API Focus** | Integração com expectativas de mercado do Relatório Focus | ⏳ Planejado | v7.0 |
| **EMBI+ em tempo real** | Derivação endógena do prêmio de risco via API | ⏳ Planejado | v7.0 |
| **Credibilidade endógena** | Modelo baseado no histórico de cumprimento da meta | ⏳ Planejado | v7.0 |
| **Choques exógenos** | Oil/TTF como variáveis de estado no modelo | ⏳ Planejado | v7.0 |
| **Intervalos de confiança** | 86% de credibilidade com derivados de incerteza | ⏳ Planejado | v7.0 |
| **Accountability total** | Derivação endógena formalizada no Lean | ⏳ Planejado | v7.0 |

---

## 📊 Matriz de Maturação

| Critério | v5.x | v6.1 | v7.0 (planejado) |
|----------|------|------|------------------|
| **Aritmética formalizada** | ✅ | ✅ | ✅ |
| **Modelo regime-dependente** | ❌ | ✅ | ✅ |
| **Prêmio de risco endógeno** | ❌ | ❌ | ✅ |
| **Credibilidade endógena** | ❌ | ❌ | ✅ |
| **Choques (oil/TTF)** | ❌ | ❌ | ✅ |
| **Intervalos de confiança** | ❌ | ❌ | ✅ |
| **Accountability total** | ❌ | ❌ | ✅ |
| **Status** | 2.0/3 | 2.75/3 | 3.0/3 |

---

## 🎯 Conclusão

O SELIX é uma **ferramenta de auditoria aritmética e transparência**, não um modelo DSGE. Seu valor está em formalizar provas e quantificar custos de oportunidade, não em substituir o COPOM.

A evolução para v7.0 trará **derivação endógena** de parâmetros, aproximando o modelo de accountability total, mantendo a honestidade intelectual sobre o que é possível em um ambiente mobile/aberto.
