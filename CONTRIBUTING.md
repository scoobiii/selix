# Contribuindo para o SELIX

## Como contribuir
1. Fork o repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`).
3. Commit suas mudanças.
4. Push e abra um Pull Request.

## Diretrizes
- Código em Python (3.10+).
- Use type hints.
- Adicione testes quando possível.
- Documente novas funções.

## Issues
- Use labels: `bug`, `enhancement`, `good first issue`.
- Descreva o problema com clareza.

## Comunicação
- Discord (link) ou Issues do GitHub.

## 📋 Backlog Atualizado (v5.1-Formal)

### ✅ Concluído (Sprint Formalização)
- **[T7] Refatoração de Constantes:** Substituição dos valores hardcoded de 6 pontos por chamadas à API de axiomas econômicos e funções de derivação dinâmica.
- **[T8/T9] Validação Numérica:** Confirmação via `norm_num` dos valores 345 bi (economia) e quantização precisa de 9,48% para 9,25%. Correção da referência biológica obsoleta (270) para o modelo econômico atual.
- **[T10] Integração SELIX_v4/v5:** Verificação das faixas de operação (~423/470-540/1,3-2,4 tri) com constante manual ajustada e $s\_star$ fixado em 6,25% conforme literatura DSGE.
- **[Gap Formal] Derivação Teórica:** Implementação de teorema que deriva os parâmetros do modelo econômico real, eliminando a dependência de "chutes" iniciais. Cobertura elevada de ~70% para ~95%.

### 📋 Próximos Passos (v5.2-Resilience)
- **[R1] Otimização de Memória:** Reduzir footprint do worker em dispositivos A23/Termux.
- **[R2] Cache Distribuído:** Implementar estratégia de cache para endpoints de alta demanda (`/v1/selic`).
