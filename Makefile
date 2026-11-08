LFLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
SGOINFRE = /sgoinfre/$(USER)

ifneq ($(shell hostname),portablepmalato)
	UV_PROJECT_ENVIRONMENT := $(SGOINFRE)/student/.venv
	UV_CACHE_DIR := $(SGOINFRE)/uv-cache
	UV_LINK_MODE := copy
	HF_HOME := $(SGOINFRE)/hugging_face
	export UV_PROJECT_ENVIRONMENT
	export UV_CACHE_DIR
	export UV_LINK_MODE 
	export HF_HOME
endif

# export /sgoinfre/$(USER)/student/.venv
# export /sgoinfre/$(USER)/uv-cache
# export copy
# export /sgoinfre/$(USER)/hugging_face


all: run

install:
	if [ "$$(hostname)" != "portablepmalato" ]; then \
		mkdir -p $(UV_CACHE_DIR) $(HF_HOME); \
	fi
	uv sync

index:
	uv run python3 -m src index --max_chunk_size 2000

search:
	uv run python3 -m src search "How to configure the OpenAI server?" --k 5

search_dataset:
	uv run python -m src search_dataset \
  	--dataset_path data/datasets/public/UnansweredQuestions/dataset_docs_public.json \
  	--k 10 \
  	--save_directory data/output/search_results/UnansweredQuestions

evaluate:
	uv run python3 -m src evaluate --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  	--dataset_path data/datasets/public/AnsweredQuestions/dataset_docs_public.json

answer:
	uv run python -m src answer "What HTTP endpoint is used to load a LoRA adapter?" --k 5

answer_dataset:
	uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --save_directory data/output/search_results_and_answer/UnansweredQuestions

run:
	make index
	make search_dataset
	make evaluate

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

.PHONY: all install index search search_dataset evaluate answer answer_dataset run debug lint lint-strict clean