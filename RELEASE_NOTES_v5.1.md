# 🚀 SELIX v5.1-Formal Release Notes

**Data:** 2026-08-04  
**Status:** ✅ Produção | **Cobertura Formal:** 95%+  

## 🎯 Destaques da Versão

### 1. Zerar o Gap Formal (T7-T10)
*   **Derivação Axiomática:** Substituição de constantes *hardcoded* por derivações baseadas na Regra de Taylor Estendida e modelos DSGE.
*   **Teorema do Mínimo Restrito:** A Selic ideal agora é o mínimo entre o Custo de Capital, Teto de Inflação e Taxa Natural ($r^*$).
*   **Quantização Operacional:** Implementação de função de piso em grid de 0,25 p.p. para aderência às normas do COPOM ($9,48\% \rightarrow 9,25\%$).

### 2. Correção de Impacto Fiscal
*   **Atualização de Base:** Economia anual recalculada de R$ 270 bi para **R$ 345 bi**, refletindo a base atual da Dívida Pública Federal (~R$ 6,9 tri).
*   **Validação Numérica:** Confirmação via `norm_num` e limpeza de referências obsoletas em bots e documentação.

### 3. Robustez e Documentação
*   **README v5.1:** Nova estrutura com tabelas de derivação formal e arquitetura de 3 camadas.
*   **Validação Automática:** Criação do script `validate_formal_gap.sh` para garantir integridade dos axiomas em futuros commits.
*   **SWOT 3/3:** Análise estratégica completa integrada ao backlog do projeto.

## 🛠️ Mudanças Técnicas
*   `agents/`: Atualização em massa de scripts de bot e RAG para refletir novos valores macroeconômicos.
*   `src/selix/`: Refatoração do motor de inferência para remover dependência de médias móveis fixas.
*   `docs/`: Whitepapers e relatórios de evidências atualizados para a versão axiomática.

## 📊 Métricas de Performance
*   **Selic Ideal Derivada:** 9,25% (vs 14,25% real).
*   **Latência (p95):** 152ms sob stress test de 80 VUs.
*   **Disponibilidade:** 24/7 via Watchdog em ambiente Termux/Android.

---
*MIT © 2026 – Zeh Sobrinho, GOS3, MEX Energia*
