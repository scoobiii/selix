# Guia de Teste de Stress - Selix

## Padrões de Mercado Simulados

| Horário | Fator | Contexto |
|---------|-------|----------|
| 09:00-12:00 | 1.5x | Abertura do mercado, maior movimento |
| 14:00-17:00 | 1.3x | Fechamento do mercado |
| 20:00-22:00 | 0.8x | Pós-mercado, análise de dados |
| 00:00-05:00 | 0.2x | Madrugada, manutenção |

## Dias da Semana

| Dia | Fator | Contexto |
|-----|-------|----------|
| Segunda | 1.2x | Acúmulo de fim de semana |
| Sexta | 0.8x | Redução antes do fim de semana |
| Fim de semana | 0.4x | Baixa atividade |

## Thresholds de Aceite

| Métrica | Limite | Status |
|---------|--------|--------|
| Taxa de sucesso | > 95% | ✅ Obrigatório |
| Tempo médio | < 500ms | ✅ Obrigatório |
| P95 | < 1000ms | ✅ Obrigatório |
| P99 | < 2000ms | ⚠️ Desejável |
| Erros 5xx | < 1% | ✅ Obrigatório |

## Comandos Rápidos

```bash
# Teste de fumaça (rápido)
python tests/stress/variable_load_test.py --duration 10 --workers 2

# Teste de carga média
python tests/stress/variable_load_test.py --duration 60 --workers 10

# Teste de estresse
python tests/stress/variable_load_test.py --duration 120 --workers 20

# Teste de pico
python tests/stress/variable_load_test.py --duration 30 --workers 50
```

