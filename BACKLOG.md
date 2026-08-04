# 📋 Backlog do Projeto SELIX

Este documento detalha as tarefas pendentes, melhorias planejadas e o roadmap para as próximas versões do SELIX.

## 🚀 Roadmap v6.0: Autonomia Total

### Prioridade Alta (Q3 2026)
- [ ] **Integração de APIs Dinâmicas (T7):** Substituir as médias de 6 pontos hardcoded por chamadas diretas às APIs do BCB (SGS) e B3 (via provedores de dados) para cálculo em tempo real.
- [ ] **CI/CD Formal:** Integrar a verificação do Lean 4 e do Z3 no fluxo de GitHub Actions para garantir que nenhum commit quebre a prova matemática.
- [ ] **Correção de "Bio" e Documentação:** Revisar todos os documentos e scripts de automação de mídias sociais para garantir consistência com a economia de R$ 345 bi/ano.

### Prioridade Média (Q4 2026)
- [ ] **Dashboard v2:** Interface web interativa para visualização dinâmica dos tetos (Taylor, ROE, Fiscal) e simulação de cenários.
- [ ] **Multi-Agent Sentiment:** Implementar um enxame de agentes para analisar o sentimento do mercado financeiro em tempo real e ajustar o prêmio de risco no modelo.
- [ ] **Resiliência de Dados:** Implementar replicação do SQLite para PostgreSQL para suportar maior carga de usuários na API.

### Prioridade Baixa (2027)
- [ ] **Relatórios PDF/A:** Geração automática de relatórios técnicos auditáveis para submissão ao Banco Central e Tesouro Nacional.
- [ ] **Internacionalização:** Tradução completa da documentação e API para Inglês e Espanhol para exportação do modelo para outros mercados emergentes.

## ✅ Concluído recentemente (v5.4.0)
- [x] **Zerar Gap Formal:** Derivação axiomática de parâmetros no Lean 4.
- [x] **Atualização de Impacto:** Recálculo da economia anual para R$ 345 bi (base 6.9 tri).
- [x] **Quantização Copom:** Implementação da lógica de grid 0.25pp no modelo formal.
- [x] **Sincronização Python/Lean:** Alinhamento das constantes entre `core.py` e `SELIX_v4.lean`.
