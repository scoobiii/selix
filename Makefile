# Makefile - selix
# Versão: 1.2.0

.PHONY: help venv requirements migrate run bot test test-load stress clean canary test-canary

help:
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make venv          → Cria o ambiente virtual"
	@echo "  make requirements  → Instala as dependências"
	@echo "  make migrate       → Roda as migrations"
	@echo "  make run           → Sobe a aplicação"
	@echo "  make bot           → Roda o bot do Bluesky"
	@echo "  make test          → Roda a suíte de testes"
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
	bash scripts/migrate_all.sh

run: migrate
	bash run_selix.sh

bot:
	cd /root/selix && bash -c "source venv/bin/activate && python agents/bluesky_bot/post_profissional.py"

# -----------------------------
# Testes
# -----------------------------
test:
	. venv/bin/activate && pytest tests/ -v --cov=confidence --cov=src

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
