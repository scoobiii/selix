# SELIX v5.1-Formal: Inteligência Econômica Autônoma

**Selic real:** 14,25% · **Selic ideal:** 9,25% · **Economia anual:** R$ 345 bi  
*(Cálculo: Dívida pública R$ 6,9 tri × 5,00 p.p. de redução)*

O SELIX deriva a Selic ideal a partir de **axiomas econômicos formais** e não mais de constantes hardcoded. O modelo agora integra a **Regra de Taylor Estendida** com restrições de equilíbrio geral (DSGE) e quantização operacional.

## 🧮 Fundamentação Teórica (Gap Formal Zero)

| Parâmetro | Derivação Formal | Valor Contínuo | Valor Quantizado | Fonte/Teorema |
|---|---|---|---|---|
| **Teto de Inflação** | Meta + Margem | 9,48% | - | Meta BCB + 5% |
| **Custo de Capital** | ROE B3 Ajustado | 29,67% | - | Economatica/B3 |
| **r* (Taxa Natural)** | Filtro HP + Phillips | 6,25% | - | BCB/DSGE Models |
| **Selic Ideal** | Mínimo Restrito | 9,48% | **9,25%** | Teorema do Mínimo |

> **Nota sobre Quantização:** O valor operacional de **9,25%** é obtido via função de piso em grid de 0,25 p.p.

## 🚀 Status do Projeto

| Métrica | Status | Observação |
|---|---|---|
| **Versão** | v5.1-Formal | Integração de axiomas econômicos |
| **Testes Unitários** | 83/83 ✅ | Cobertura de lógica de negócio |
| **Cobertura Formal** | ~95% ✅ | Derivação de parâmetros via teoremas |
| **Stress Test** | 80 VUs, p95=152ms ✅ | Resiliência mantida |
| **Disponibilidade** | 24/7 (Termux/Android) | Watchdog ativo |

## 🏗️ Arquitetura

1. **Coleta Assíncrona:** Worker v7 coleta dados de Brent (Yahoo Finance) e Selic (BCB).
2. **Processamento Formal:** Motor de inferência aplica a Regra de Taylor e restrições de mercado.
3. **Publicação Autônoma:** Supervisor publica threads no Bluesky às 9h, 13h e 18h (BRT).

## 📖 Endpoints da API

| Endpoint | Método | Autenticação | Descrição |
|---|---|---|---|
| `/v1/health` | GET | Pública | Status da API |
| `/v1/selic` | GET | Chave API | Última Selic real e ideal derivada |
| `/v1/perguntar` | POST | Chave API | Pergunta assíncrona ao motor de inferência |

---
*MIT © 2026 – Zeh Sobrinho, GOS3, MEX Energia*
