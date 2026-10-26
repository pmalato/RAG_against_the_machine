LFLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
SGOINFRE = /sgoinfre/pecoelho

ifneq ($(shell hostname),portablepmalato)
	UV_PROJECT_ENVIRONMENT := $(SGOINFRE)/venv-rag
	UV_CACHE_DIR := $(SGOINFRE)/uv-cache
	UV_LINK_MODE := copy
	HF_HOME := $(SGOINFRE)/hugging_face
	export UV_PROJECT_ENVIRONMENT
	export UV_CACHE_DIR
	export UV_LINK_MODE 
	export HF_HOME
endif

all: run

install:
	if [ "$$(hostname)" != "portablepmalato" ]; then \
		mkdir -p $(UV_CACHE_DIR) $(HF_HOME); \
	fi
	uv sync

run:
	uv run python3 -m src

debug:
	uv run python3 pdb -m src

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