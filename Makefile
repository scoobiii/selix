.PHONY: venv requirements run clean

venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip

requirements: venv
	. venv/bin/activate && pip install -r requirements.txt

run: requirements
	./run_selix.sh

clean:
	rm -rf venv selix.db worker.log __pycache__
	find . -name "*.pyc" -delete
