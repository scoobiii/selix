
# SELIX DevOps Guide v4.0

## 📐 Arquitetura

```

```

## ⚙️ Requisitos

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| **CPU** | 2 núcleos | 4+ núcleos |
| **RAM** | 2 GB | 4+ GB |
| **Disco** | 10 GB | 20 GB SSD |
| **Python** | 3.12+ | 3.13 |
| **Rede** | 1 Mbps | 10+ Mbps |

## 🔧 Instalação Completa (Produção)

```bash
# 1. Clone o repositório
git clone https://github.com/scoobiii/selix.git
cd selix

# 2. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
nano .env   # preencha com as credenciais reais (ver seção abaixo)

# 5. Execute migração do banco
make migrate

# 6. Otimize SQLite para produção (se usar SQLite)
sqlite3 selix.db <<'SQL'
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=MEMORY;
PRAGMA wal_autocheckpoint=1000;
SQL

# 7. Inicie os serviços
make run
```

🔑 Variáveis de Ambiente (obrigatórias e opcionais)

Variável Obrigatória Padrão Descrição
OILPRICEAPI_KEY ✅ – Chave da API de preços de petróleo
BLUESKY_USERNAME ✅ – Usuário do Bluesky (ex: user.bsky.social)
BLUESKY_APP_PASSWORD ✅ – Senha de aplicativo do Bluesky
SELIX_DB_PATH ❌ /app/selix.db Caminho do banco SQLite
WORKER_INTERVAL_SEC ❌ 300 Intervalo de coleta do worker (segundos)
LOG_LEVEL ❌ INFO Nível de log (DEBUG, INFO, WARNING, ERROR)
OLLAMA_URL (opcional) ❌ http://localhost:11434 URL do Ollama (LLM local)

Arquivo .env exemplo:

```env
SELIX_DB_PATH=/data/selix.db
WORKER_INTERVAL_SEC=300
LOG_LEVEL=INFO
OILPRICEAPI_KEY=abc123def456
BLUESKY_USERNAME=selix.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

📦 Comandos Make (Completos)

```makefile
.PHONY: venv requirements migrate run bot test test-load stress clean deploy

venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip

requirements: venv
	. venv/bin/activate && pip install -r requirements.txt

migrate: requirements
	bash scripts/migrate_all.sh

run: migrate
	bash run_selix.sh

bot:
	cd /root/selix && bash -c "source venv/bin/activate && python agents/bluesky_bot/post_profissional.py"

test:
	. venv/bin/activate && pytest tests/ -v --cov=confidence --cov=src --cov-report=term --cov-report=html

test-load:
	k6 run tests/load_test.js

stress:
	k6 run tests/stress_test.js

clean:
	rm -rf venv logs/*.log __pycache__ .pytest_cache htmlcov
	find . -name "*.pyc" -delete

deploy: clean migrate
	systemctl restart selix-api selix-worker
```

🧪 Testes Automatizados

Testes Unitários (pytest)

```bash
make test
# Relatório de cobertura: htmlcov/index.html
```

Testes de Carga (k6)

```bash
# Instalar k6 (se não tiver)
wget -q https://github.com/grafana/k6/releases/download/v0.52.0/k6-v0.52.0-linux-arm64.tar.gz
tar -xzf k6-v0.52.0-linux-arm64.tar.gz
sudo mv k6-v0.52.0-linux-arm64/k6 /usr/local/bin/

# Executar
make test-load   # até 100 VUs
make stress      # até 500 VUs
```

🐳 Deploy com Docker (Produção)

Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SELIX_DB_PATH=/data/selix.db
VOLUME ["/data", "/logs"]
CMD ["python", "src/api/main_v4.py"]
```

docker-compose.yml

```yaml
version: '3.8'
services:
  api:
    build: .
		    ports:
		      - "5000:5000"
		    environment:
		      - SELIX_DB_PATH=/data/selix.db
		      - OILPRICEAPI_KEY=${OILPRICEAPI_KEY}
		    volumes:
		      - ./data:/data
		      - ./logs:/logs
		    restart: unless-stopped
		    command: gunicorn -w 4 -b 0.0.0.0:5000 src.api.main_v4:app

		  worker:
		    build: .
		    environment:
		      - SELIX_DB_PATH=/data/selix.db
		      - OILPRICEAPI_KEY=${OILPRICEAPI_KEY}
		    volumes:
		      - ./data:/data
		      - ./logs:/logs
		    restart: unless-stopped
		    command: python src/selix/worker_v4.py

		  nginx:
		    image: nginx:alpine
		    ports:
		      - "80:80"
		    volumes:
		      - ./nginx_selix.conf:/etc/nginx/conf.d/default.conf
		    depends_on:
		      - api
		    restart: unless-stopped
		```

		Subir tudo:

		```bash
		docker-compose up -d
		```

		📊 Monitoramento e Logs

	Serviço Arquivo de log Comando para monitorar
	API /root/selix/logs/api.log tail -f /root/selix/logs/api.log
	Worker /root/selix/logs/worker.log tail -f /root/selix/logs/worker.log
	Risco geoenergético /root/selix/logs/geo_risk.log tail -f /root/selix/logs/geo_risk.log
	Respostas do Bluesky /root/selix/logs/mencoes.log tail -f /root/selix/logs/mencoes.log
	Cron /root/selix/logs/selix_cron.log tail -f /root/selix/logs/selix_cron.log

Métricas de saúde

```bash
# Verificar API
curl -s http://localhost:5000/v1/health | jq .

# Verificar worker
ps aux | grep worker_v4 | grep -v grep

# Verificar banco
sqlite3 /root/selix/selix.db "SELECT COUNT(*) FROM commodities;"
```

🔄 CI/CD com GitHub Actions

Crie .github/workflows/ci.yml:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run unit tests
      run: pytest tests/ -v

    - name: Run coverage
      run: pytest --cov=confidence --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        flags: unittests

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run Bandit
      run: |
        pip install bandit
        bandit -r src/ -f json -o bandit_report.json
    - name: Upload Bandit report
      uses: actions/upload-artifact@v4
      with:
        name: bandit-report
        path: bandit_report.json
```

🧠 Otimizações para Produção

SQLite → PostgreSQL (quando necessário)

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Criar banco
sudo -u postgres psql -c "CREATE DATABASE selix_prod;"

# Migrar dados
pg_dump selix.db > selix.sql
psql -d selix_prod < selix.sql
```

Cache Redis para endpoints frequentes

```python
import redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_cached_or_compute(key, ttl=60):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    result = compute_expensive()
    redis_client.setex(key, ttl, json.dumps(result))
    return result
```

Rate Limiting (NGINX)

```nginx
http {
    limit_req_zone $binary_remote_addr zone=selix:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    server {
        listen 80;
        location /v1/ {
            limit_req zone=selix burst=20 nodelay;
            limit_conn addr 10;
            proxy_pass http://selix_backend;
        }
    }
}
```

🚨 Troubleshooting Comum

	Problema Sintoma Solução
	API não inicia Port 5000 already in use pkill -f main_v4 ou fuser -k 5000/tcp
	Worker não insere Brent Log: falha ao obter dado real Verifique chave OILPRICEAPI_KEY e internet
	SQLite database is locked Erro 500 na API Execute PRAGMA journal_mode=WAL;
	Bot não posta ModuleNotFoundError pip install -r requirements.txt
	Latência alta p95 > 1s Ative WAL, aumente cache, use Redis
	LLM local não responde Timeout Verifique se Ollama está rodando: systemctl status ollama

	📅 Manutenção Periódica

	Tarefa Frequência Comando
	Atualizar dependências Mensal pip install --upgrade -r requirements.txt
	Limpar logs antigos Semanal find logs/ -name "*.log" -mtime +7 -delete
	Fazer backup do banco Diário sqlite3 selix.db ".backup backup_$(date +%Y%m%d).db"
	Verificar uso de disco Semanal df -h && du -sh /root/selix
	Rodar testes de carga Quinzenal make test-load
	Auditar segurança Trimestral bandit -r src/

🔗 Referências

· Repositório principal
· Documentação da API
· Bluesky Bot
· OilPriceAPI

---

