# Visualizações da SELIX

Esta pasta conterá gráficos e infográficos gerados a partir dos dados do projeto.

## Sugestões de gráficos
1. `selic_vs_selix.png` – Comparação da Selic atual (14,50%) vs SELIX (9,25%)
2. `juro_real_historico.png` – Evolução do juro real nos últimos 12 meses
3. `convergencia.png` – Projeção de convergência em 10,5 meses (cortes de 0,5%)
4. `roe_vs_selic.png` – ROE do IBOVESPA (31,23%) vs Selic/SELIX
5. `impacto_pib.png` – Impacto no PIB per capita (aumento de R$ 14.900)

## Comandos para gerar (exemplo com matplotlib)
```python
import matplotlib.pyplot as plt
plt.bar(['Selic atual', 'SELIX'], [14.5, 9.25])
plt.ylabel('Taxa (%)')
plt.title('Comparação Selic atual vs SELIX')
plt.savefig('selic_vs_selix.png')
\```
