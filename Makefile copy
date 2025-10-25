# Makefile — MCP Gateway Workshop (uv-based, no pip)
# Cross-platform: Windows (PowerShell/CMD/Git Bash) + macOS/Linux
# - `make install`:
#     * checks for Python ≥ REQUIRED_PYTHON
#     * if not found, runs scripts/install.sh exactly once to install it
#     * then creates/syncs .venv with uv and installs the project
# - Dev tools run via `uv run --with ...` to avoid polluting project deps.

.DEFAULT_GOAL := install

# =============================================================================
#  OS detection & shell configuration
# =============================================================================

ifeq ($(OS),Windows_NT)
SHELL         := powershell.exe
.SHELLFLAGS   := -NoProfile -ExecutionPolicy Bypass -Command
NULL_DEVICE   := $$null
OK            := Write-Host
ERR           := Write-Error
BASH          := bash
PATH_SEP      := \\
else
SHELL         := /bin/bash
.ONESHELL:
.SHELLFLAGS   := -eu -o pipefail -c
NULL_DEVICE   := /dev/null
OK            := echo
ERR           := echo >&2
BASH          := bash
PATH_SEP      := /
endif

# =============================================================================
#  Settings
# =============================================================================

VENV              ?= .venv
REQUIRED_PYTHON   ?= 3.11

# Optional book build settings (safe to ignore if not used)
BOOK_DIR          ?= book
MANUSCRIPT        ?= $(BOOK_DIR)/manuscript.md
EPUB_OUT          ?= $(BOOK_DIR)/book.epub
PDF_OUT           ?= $(BOOK_DIR)/book.pdf
ZIP_OUT           ?= book.zip
COVER_IMG         ?= $(BOOK_DIR)/kindle/cover/cover.jpg
IMAGES_DIR        ?= $(BOOK_DIR)/images

.PHONY: help install venv update lint format test docs-serve docs-build token \
        up down seed clean check-uv maybe-bootstrap python-version \
        book book-epub book-pdf book-zip

# =============================================================================
#  Help
# =============================================================================

help:
	@$(OK) "Common targets:"
	@$(OK) "  make install        - ensure Python ≥ $(REQUIRED_PYTHON) (auto-install if missing), then uv sync"
	@$(OK) "  make venv           - create .venv with uv (uses Python $(REQUIRED_PYTHON))"
	@$(OK) "  make update         - re-sync dependencies with uv"
	@$(OK) "  make lint           - ruff + black check + mypy (via uv)"
	@$(OK) "  make format         - run black + ruff --fix (via uv)"
	@$(OK) "  make test           - run pytest with coverage (via uv)"
	@$(OK) "  make docs-serve     - mkdocs serve (via uv)"
	@$(OK) "  make docs-build     - mkdocs build --strict (via uv)"
	@$(OK) "  make token          - create demo JWT"
	@$(OK) "  make up             - docker compose up -d"
	@$(OK) "  make down           - docker compose down -v"
	@$(OK) "  make seed           - register adapter with gateway"
	@$(OK) "  make clean          - remove venv & caches"
	@$(OK) "  make python-version - print detected Python version"
	@$(OK) "  ---"
	@$(OK) "  make book           - build EPUB + PDF from book/manuscript.md and zip the /book folder"
	@$(OK) "  make book-epub      - build only EPUB"
	@$(OK) "  make book-pdf       - build only PDF"
	@$(OK) "  make book-zip       - zip the /book folder (for release upload)"

# =============================================================================
#  Bootstrap (only runs installer if Python ≥ $(REQUIRED_PYTHON) is NOT found)
# =============================================================================

maybe-bootstrap:
ifeq ($(OS),Windows_NT)
	@$$ok = $$false; \
	$$req = '$(REQUIRED_PYTHON)'.Split('.'); $$majReq = [int]$$req[0]; $$minReq = [int]$$req[1]; \
	if (Get-Command py -ErrorAction SilentlyContinue) { \
	  & py -$(REQUIRED_PYTHON) -V *> $(NULL_DEVICE); if ($$LASTEXITCODE -eq 0) { $$ok = $$true } \
	}; \
	if (-not $$ok -and (Get-Command python -ErrorAction SilentlyContinue)) { \
	  $$ver = (& python -V) 2>&1; if ($$ver -match '(\d+)\.(\d+)') { \
	    $$maj=[int]$$Matches[1]; $$min=[int]$$Matches[2]; \
	    if ($$maj -gt $$majReq -or ($$maj -eq $$majReq -and $$min -ge $$minReq)) { $$ok = $$true } \
	  } \
	}; \
	if ($$ok) { \
	  Write-Host "✅ Python ≥ $(REQUIRED_PYTHON) detected"; \
	} else { \
	  Write-Host "ℹ️  Python ≥ $(REQUIRED_PYTHON) not found — running scripts$(PATH_SEP)install.sh"; \
	  if (Get-Command $(BASH) -ErrorAction SilentlyContinue) { & $(BASH) scripts/install.sh } \
	  else { Write-Error "Git Bash not found. Please install Git for Windows to run scripts/install.sh."; exit 1 } \
	}
else
	@if command -v python$(REQUIRED_PYTHON) >$(NULL_DEVICE) 2>&1; then \
	  echo "✅ Python ≥ $(REQUIRED_PYTHON) detected (python$(REQUIRED_PYTHON))"; \
	elif command -v python3 >$(NULL_DEVICE) 2>&1 && \
	     python3 -c "import sys; import os; req=tuple(map(int,'$(REQUIRED_PYTHON)'.split('.'))); sys.exit(0 if sys.version_info[:2]>=req else 1)" \
	     >$(NULL_DEVICE) 2>&1; then \
	  echo "✅ Python ≥ $(REQUIRED_PYTHON) detected (python3)"; \
	else \
	  echo "ℹ️  Python ≥ $(REQUIRED_PYTHON) not found — running scripts/install.sh"; \
	  $(BASH) scripts/install.sh; \
	fi
endif

# =============================================================================
#  Ensure uv is available (installs if missing)
# =============================================================================

check-uv:
ifeq ($(OS),Windows_NT)
	@$$cmd = Get-Command uv -ErrorAction SilentlyContinue; \
	if (-not $$cmd) { \
	  Write-Host "Info: 'uv' not found. Installing..."; \
	  iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex; \
	  $$localBin = Join-Path $$env:USERPROFILE '.local\bin'; \
	  if (Test-Path $$localBin) { $$env:Path = "$$localBin;$$env:Path" } \
	}; \
	$$cmd = Get-Command uv -ErrorAction SilentlyContinue; \
	if (-not $$cmd) { Write-Error "'uv' is not available after installation."; exit 1 } \
	else { Write-Host "✅ uv is available." }
else
	@command -v uv >$(NULL_DEVICE) 2>&1 || ( \
	  echo "Info: 'uv' not found. Installing..."; \
	  curl -LsSf https://astral.sh/uv/install.sh | sh; \
	); \
	command -v uv >$(NULL_DEVICE) 2>&1 || { echo "Error: 'uv' is not available after installation." >&2; exit 1; }; \
	echo "✅ uv is available."
endif

# =============================================================================
#  Core: install / venv / update  (uv only, no pip)
# =============================================================================

## Create/sync environment and install project (editable) using uv
install: check-uv maybe-bootstrap
	@uv sync --python $(REQUIRED_PYTHON)
	@$(OK) "✅ Environment ready in $(VENV)."
	@$(OK) "   Activate on Unix:    source $(VENV)$(PATH_SEP)bin$(PATH_SEP)activate"
	@$(OK) "   Activate on Windows: .\\$(VENV)\\Scripts\\Activate.ps1"

## Create just the .venv with Python $(REQUIRED_PYTHON) (no deps)
venv: check-uv maybe-bootstrap
	@uv venv --python $(REQUIRED_PYTHON)
	@$(OK) "✅ Created $(VENV)."

## Re-sync dependencies (re-resolve / reinstall as needed)
update: check-uv
	@uv sync

# =============================================================================
#  Dev / QA (tools provided on-the-fly via uv --with)
# =============================================================================

lint:
	@uv run --with ruff --with black --with mypy -- ruff check src tests
	@uv run --with ruff --with black --with mypy -- black --check src tests
	@uv run --with ruff --with black --with mypy -- mypy src

format:
	@uv run --with ruff --with black -- ruff check --fix src tests
	@uv run --with ruff --with black -- black src tests

test:
	@uv run --with pytest -- pytest -q --disable-warnings --maxfail=1 --cov=src --cov-report=term-missing

# =============================================================================
#  Docs (mkdocs via uv)
# =============================================================================

docs-serve:
	@uv run --with mkdocs --with "mkdocs-material[imaging]" -- mkdocs serve


docs-build:
	@uv run --with mkdocs --with "mkdocs-material[imaging]" -- mkdocs build --strict


# =============================================================================
#  Project scripts / docker
# =============================================================================

token:
	@uv run -- python scripts/create_jwt.py --sub admin@example.com --role analyst --secret dev-secret

up:
	@docker compose up -d

down:
	@docker compose down -v

seed:
	@uv run -- $(BASH) scripts/seed_gateway.sh

# =============================================================================
#  BOOK BUILDS (Kindle-ready EPUB + PDF + ZIP)
# =============================================================================

## Master target: build EPUB, then PDF, then a distributable zip
book: book-epub book-pdf book-zip
	@$(OK) "📚 Done: $(EPUB_OUT), $(PDF_OUT), $(ZIP_OUT)"

## Build EPUB only
book-epub:
	@test -f "$(MANUSCRIPT)" || { $(ERR) "Missing $(MANUSCRIPT)"; exit 1; }
	@uv run \
		--with ebooklib \
		--with markdown \
		--with pillow \
		-- python scripts/build_book.py \
		--input "$(MANUSCRIPT)" \
		--epub "$(EPUB_OUT)" \
		--cover "$(COVER_IMG)" \
		--images-dir "$(IMAGES_DIR)"
	@$(OK) "✅ EPUB: $(EPUB_OUT)"

## Build PDF only (WeasyPrint if available; fallback to ReportLab)
book-pdf:
	@test -f "$(MANUSCRIPT)" || { $(ERR) "Missing $(MANUSCRIPT)"; exit 1; }
	@uv run \
		--with markdown \
		--with weasyprint \
		--with reportlab \
		--with pillow \
		-- python scripts/build_book.py \
		--input "$(MANUSCRIPT)" \
		--pdf "$(PDF_OUT)" \
		--cover "$(COVER_IMG)" \
		--images-dir "$(IMAGES_DIR)"
	@$(OK) "✅ PDF: $(PDF_OUT)"

## Zip the entire /book folder for upload/release (portable, no heredoc)
book-zip:
	@test -d "$(BOOK_DIR)" || { $(ERR) "Missing $(BOOK_DIR) directory"; exit 1; }
	@uv run -- python -c "import os, zipfile; root='$(BOOK_DIR)'; out='$(ZIP_OUT)'; z=zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED); \
from os.path import join, relpath; \
[ z.write(join(b,f), arcname=relpath(join(b,f), root)) for b,_,fs in os.walk(root) for f in fs ]; \
z.close(); print('Zipped -> ' + out)"
	@$(OK) "✅ ZIP: $(ZIP_OUT)"

# =============================================================================
#  Utilities
# =============================================================================

python-version:
ifeq ($(OS),Windows_NT)
	@if (Get-Command py -ErrorAction SilentlyContinue) { & py -V } \
	else { if (Get-Command python -ErrorAction SilentlyContinue) { & python -V } else { Write-Host "Python not found." } }
else
	@command -v python$(REQUIRED_PYTHON) >/dev/null 2>&1 && python$(REQUIRED_PYTHON) -V || \
	(command -v python3 >/dev/null 2>&1 && python3 -V || echo "Python not found.")
endif

clean:
ifeq ($(OS),Windows_NT)
	@Write-Host "Cleaning..."
	@if (Test-Path '$(VENV)') { Remove-Item -Recurse -Force '$(VENV)' }
	@Remove-Item -Recurse -Force -ErrorAction SilentlyContinue .pytest_cache, .mypy_cache, .ruff_cache, dist, build
	@Get-ChildItem -Recurse -Force -Include *.egg-info | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
	@Get-ChildItem -Recurse -Force -Directory -Filter __pycache__ | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
	@Write-Host "✅ Clean complete."
else
	@echo "Cleaning..."
	@rm -rf "$(VENV)" .pytest_cache .mypy_cache .ruff_cache dist build *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✅ Clean complete."
endif
