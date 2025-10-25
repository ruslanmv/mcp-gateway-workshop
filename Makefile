.PHONY: venv install format lint test up down logs token

venv:
	python3 -m venv .venv && . .venv/bin/activate && pip install -U pip

install:
	. .venv/bin/activate && pip install -r requirements.txt && pip install -e .

format:
	. .venv/bin/activate && black . && ruff check --fix .

lint:
	. .venv/bin/activate && ruff check . && mypy src

test:
	. .venv/bin/activate && pytest -q

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f

token:
	python scripts/create_jwt.py --sub admin@example.com --secret dev-secret
