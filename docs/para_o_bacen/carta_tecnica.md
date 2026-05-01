# CARTA TÉCNICA AO BANCO CENTRAL

**Assunto:** Prova Matemática da SELIX - Solicitação de Análise

**Data:** 01 de maio de 2026

## Resumo Executivo

O modelo SELIX demonstra que a Taxa Selic ideal é **9.25%**, não 14.50%.

### Os 5 Teoremas Provados

| Teorema | Resultado | Implicação |
|---------|-----------|------------|
| 1 | 9.25% ≤ 9.99% | Investment Grade (BBB+) |
| 2 | 9.25% ≤ 29.67% | Não canibaliza produção |
| 3 | 4.77% ≤ 5% | Tesouro paga principal |
| 4 | 14.5% → 9.25% | Convergência em 10.5 meses |
| 5 | SAT | Sistema consistente |

### Metodologia

- Z3 SMT Solver (Microsoft Research)
- Lean 4 (Provador Interativo)
- Python + pytest (Testes unitários)
- Dados oficiais do BCB (SGS)

### Solicitação

1. Audiência técnica para apresentação
2. Validação independente pelo corpo técnico
3. Publicação da contraprova, se existir

**Anexos:** Código fonte, provas formais, certificados
