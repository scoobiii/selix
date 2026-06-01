.PHONY: venv requirements migrate run bot test test-load stress clean

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
	. venv/bin/activate && pytest tests/ -v --cov=confidence --cov=src

test-load:
	k6 run tests/load_test.js

stress:
	k6 run tests/stress_test.js

clean:
	rm -rf venv logs/*.log __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
