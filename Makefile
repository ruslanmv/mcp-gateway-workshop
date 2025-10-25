
# Makefile — MCP Gateway Workshop
PY ?= python3
PIP ?= pip
VENV ?= .venv
ACT := . $(VENV)/bin/activate;

.PHONY: help
help:
	@echo "Common targets:"
	@echo "  make venv           - create virtualenv"
	@echo "  make install        - install package & dev deps"
	@echo "  make lint           - ruff + black check + mypy"
	@echo "  make format         - run black + ruff --fix"
	@echo "  make test           - run pytest with coverage"
	@echo "  make docs-serve     - mkdocs serve (local docs)"
	@echo "  make docs-build     - mkdocs build --strict"
	@echo "  make token          - create demo JWT"
	@echo "  make up             - docker compose up -d"
	@echo "  make down           - docker compose down -v"
	@echo "  make seed           - register adapter with gateway"
	@echo "  make clean          - remove venv & pyc"

venv:
	$(PY) -m venv $(VENV)

install: venv
	$(ACT) $(PIP) install -U pip
	$(ACT) $(PIP) install -r requirements.txt
	$(ACT) $(PIP) install -e .

lint:
	$(ACT) ruff check src tests
	$(ACT) black --check src tests
	$(ACT) mypy src

format:
	$(ACT) ruff check --fix src tests
	$(ACT) black src tests

test:
	$(ACT) pytest -q --disable-warnings --maxfail=1 --cov=src --cov-report=term-missing

docs-serve:
	$(ACT) mkdocs serve

docs-build:
	$(ACT) mkdocs build --strict

token:
	$(ACT) $(PY) scripts/create_jwt.py --sub admin@example.com --role analyst --secret dev-secret

up:
	docker compose up -d

down:
	docker compose down -v

seed:
	$(ACT) bash scripts/seed_gateway.sh

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
	find . -name "__pycache__" -type d -exec rm -rf {} +
