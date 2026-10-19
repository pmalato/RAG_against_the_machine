LFLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
SGOINFRE = ~/sgoinfre

export UV_PROJECT_ENVIRONMENT = $(SGOINFRE)/venv-rag
export UV_CACHE_DIR = $(SGOINFRE)/uv-cache
export UV_LINK_MODE = copy
export HF_HOME = $(SGOINFRE)/hugging_face

all: run

install:
	mkdir -p $(UV_CACHE_DIR) $(HF_HOME)
	uv sync

run:
	uv run python3 src/

debug:
	uv run python3 pdb -m src/

lint:
	uv run python3 -m flake8 src
	uv run python3 -m mypy src $(LFLAGS)

lint-strict:
	uv run python3 -m flake8 src
	uv run python3 -m mypy src --strict

clean:
	rm -fr __pycache__
	rm -fr .mypy_cache
	rm -fr src/__pycache__

.PHONY: all install run debug lint lint-strict clean