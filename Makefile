# Makefile - selix
# Versão: 1.3.0

# Variáveis de ambiente (caminhos e credenciais)
DB_PATH ?= /root/selix/selix.db
API_MODULE = src/api/main_v4_fixed.py
API_LOG = /tmp/api.log
API_PID = /tmp/selix_api.pid

.PHONY: help venv requirements migrate run bot test test-load stress clean canary test-canary

help:
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make venv          → Cria o ambiente virtual"
	@echo "  make requirements  → Instala as dependências"
	@echo "  make migrate       → Roda as migrations"
	@echo "  make run           → Sobe a aplicação em foreground"
	@echo "  make run-bg        → Sobe a aplicação em background"
	@echo "  make stop          → Para a aplicação"
	@echo "  make bot           → Roda o bot do Bluesky"
	@echo "  make test          → Roda a suíte de testes (com infra automática)"
	@echo "  make test-only     → Roda apenas os testes (sem subir infra)"
	@echo "  make test-load     → Teste de carga (k6)"
	@echo "  make stress        → Teste de stress (k6)"
	@echo "  make canary        → Gera um novo teste canário"
	@echo "  make test-canary   → Gera + roda só o canário"
	@echo "  make clean         → Limpa arquivos temporários"
	@echo ""

# -----------------------------
# Ambiente
# -----------------------------
venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip

requirements: venv
	. venv/bin/activate && pip install -r requirements.txt

# -----------------------------
# Aplicação
# -----------------------------
migrate: requirements
	python scripts/init_db.py

run: migrate
	export SELIX_DB_PATH=$(DB_PATH) && \
	export MASTER_API_KEY=master_123_super_secret && \
	export SELIX_API_KEYS=test_api_key_123 && \
	PYTHONPATH=$(PWD) python $(API_MODULE)

run-bg: migrate
	@echo "🚀 Subindo API em background..."
	@( \
		export SELIX_DB_PATH=$(DB_PATH); \
		export MASTER_API_KEY=master_123_super_secret; \
		export SELIX_API_KEYS=test_api_key_123; \
		PYTHONPATH=$(PWD) nohup python $(API_MODULE) >> $(API_LOG) 2>&1 & \
		echo $$! > $(API_PID) \
	)
	@sleep 3
	@if curl -s http://localhost:5000/v1/health > /dev/null; then \
		echo "✅ API no ar (PID: $$(cat $(API_PID)))"; \
	else \
		echo "❌ API falhou ao subir. Log:"; \
		cat $(API_LOG); \
		exit 1; \
	fi
stop:
	@echo "🛑 Parando API..."
	@pkill -f "$(API_MODULE)" 2>/dev/null || true
	@rm -f $(API_PID)

bot:
	cd /root/selix && bash -c "source venv/bin/activate && python agents/bluesky_bot/post_profissional.py"

# -----------------------------
# Testes
# -----------------------------
test: requirements migrate run-bg
	@export SELIX_API_KEYS=test_api_key_123
	@export MASTER_API_KEY=master_123_super_secret
	@export SELIX_DB_PATH=$(DB_PATH)
	@echo "🧪 Rodando testes..."
	@. venv/bin/activate && pytest tests/ -v --cov=confidence --cov=src --tb=short
	@$(MAKE) stop
test-only:
	. venv/bin/activate && pytest tests/ -v --cov=confidence --cov=src --tb=short

test-load:
	k6 run tests/load_test.js

stress:
	k6 run tests/stress_test.js

# -----------------------------
# Canary
# -----------------------------
canary:
	. venv/bin/activate && python scripts/canary_test.py

test-canary: canary
	. venv/bin/activate && pytest tests/ -v -k canary

# -----------------------------
# Limpeza
# -----------------------------
clean:
	rm -rf venv logs/*.log __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	rm -f tests/test_canary_*.py
	rm -f $(API_PID) $(API_LOG)
fastapi: requirements
	@echo "🚀 Subindo FastAPI (Uvicorn) com 4 workers..."
	@uvicorn src.api.main_v4_fastapi:app --host 0.0.0.0 --port 5000 --workers 4
