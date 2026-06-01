.PHONY: venv requirements run docker-up docker-down clean

venv:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip

requirements: venv
	. venv/bin/activate && pip install -r requirements.txt

run: requirements
	./run_selix.sh

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	rm -rf venv selix.db worker.log api.log __pycache__ *.pyc
	find . -name "*.pyc" -delete
