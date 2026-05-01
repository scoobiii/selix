.PHONY: install test run clean all

install:
	pip3 install -r requirements.txt || pip install -r requirements.txt

test:
	pytest tests/ -v

run:
	python3 src/selix/core.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache

all: install test run
	@echo "✅ SELIX - Todos os testes passaram!"
