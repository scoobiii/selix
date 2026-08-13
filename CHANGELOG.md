## [v7.2.2] - 2026-08-11

### Adicionado
- Publicador canônico de snapshot no Bluesky via GitHub Actions
- Workflow `bluesky_ci.yml` (roda 2x por dia + disparo manual)
- Script `scripts/bluesky_ci_publisher.py` com Fonte Única de Verdade (`src.selix.config`)
- Política de falha visível: se o import do config quebrar, o bot **não** posta número de fallback

### Observação
- O bot atual publica apenas o snapshot oficial.
- Agente de respostas automáticas / monitoramento de menções ainda não está ativo.

# Changelog

## [v7.2.1] - 2026-08-09

### Corrigido
- DB_PATH configurável via SELIX_DB_PATH em 0 arquivos
- LOG_DIR configurável via SELIX_LOG_DIR em 0 arquivos
- main_v4_fixed.py como entrypoint da API
- Schema do banco completo (8 tabelas)
- Autenticação via SELIX_API_KEYS com fallback
- Rotas dos testes alinhadas com a API real

### Adicionado
- Workflow GitHub Actions com Redis
- scripts/init_db.py com schema completo

### Pendente
- test_alertas_geral SKIPPED
- ~50 arquivos com /root/selix hardcoded
## [v7.2.3] - 2026-08-11

### Limpeza
- Removido whitepaper.md com dados desatualizados (9,25%).
- Substituído pela nova seção de Lastro Acadêmico e endpoint DSGE Kalman.


## [v8.0.0-alpha] - 2026-08-13

### 🚀 Nova Estratégia de Produto
- Evolução do SELIX para um **ecossistema de inteligência econômica**.
- O `selix-official.json` agora é o **artefato oficial** gerado pelo sistema (Fonte Única de Verdade).
- Estrutura de monetização definida (FREE/PRO/ENTERPRISE).

### 🏗️ Arquitetura
- O cálculo é centralizado no SELIX Engine.
- Planejamento de WASM para simulações interativas no navegador.
- Distribuição via GitHub Pages (estático) + VPS/Cloud Run (API/Enterprise).

## [v8.0.0-alpha] - 2026-08-13

### 🚀 Nova Estratégia de Produto
- Evolução do SELIX para um **ecossistema de inteligência econômica**.
- O `selix-official.json` agora é o **artefato oficial** gerado pelo sistema (Fonte Única de Verdade).
- Estrutura de monetização definida (FREE / PRO / ENTERPRISE).

### 🏗️ Arquitetura
- Cálculo centralizado no SELIX Engine.
- Planejamento de WASM para simulações interativas no navegador.
- Distribuição via GitHub Pages (estático) + VPS/Cloud Run (API/Enterprise).
