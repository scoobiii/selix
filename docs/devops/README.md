# SELIX DevOps Guide

## Arquitetura

```

NGINX (rate limit) → Gunicorn (workers) → Flask API → SQLite/Postgres
↓
Workers Async
↓
OilPriceAPI | BCB | Yahoo Finance

```

## Requisitos

- Python 3.12+
- SQLite 3 (ou PostgreSQL para produção)
- 4GB RAM (recomendado)

## Instalação para Desenvolvimento

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
make venv
make requirements
make migrate
make run
```

Comandos Make

Comando Descrição
make venv Cria ambiente virtual
make requirements Instala dependências
make migrate Executa migração do banco
make run Inicia API + worker
make bot Executa bot do Bluesky
make test Executa testes unitários
make test-load Executa testes de carga (k6)
make clean Limpa cache e logs

Variáveis de Ambiente

```env
SELIX_DB_PATH=/app/selix.db
WORKER_INTERVAL_SEC=300
LOG_LEVEL=INFO
OILPRICEAPI_KEY=sua_chave
BLUESKY_USERNAME=seu_usuario
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

Testes

```bash
# Unitários
pytest tests/ -v --cov=confidence --cov=src

# Carga (k6)
k6 run tests/load_test.js

# Estresse
k6 run tests/stress_test.js
```

Deploy com Docker

```bash
docker build -t selix .
docker-compose up -d
```

Monitoramento

Logs em /root/selix/logs/:

· worker.log – coleta de dados
· api.log – requisições HTTP
· geo_risk.log – risco geoenergético

Otimização SQLite para produção

```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=MEMORY;
```

Migrando para PostgreSQL

```bash
pg_dump selix.db > selix.sql
psql -d selix_prod < selix.sql
```

CI/CD (GitHub Actions)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
```

