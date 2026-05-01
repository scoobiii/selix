.PHONY: install test run clean all venv

venv:
	python3 -m venv selix-env
	@echo "Ambiente virtual criado. Execute: source selix-env/bin/activate"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest

test:
	pytest tests/ -v

run:
	python src/selix/core.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf selix-env

all: install test run
	@echo "✅ SELIX - Todos os testes passaram!"
