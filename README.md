*This project has been created as part of the 42 curriculum by pecoelho.*

# RAG against the machine

A Retrieval-Augmented Generation (RAG) system that answers questions about the [vLLM](https://github.com/vllm-project/vllm) codebase (v0.10.1). It indexes the repository, retrieves the most relevant snippets for a question with BM25, and hands them to a small local model (`Qwen/Qwen3-0.6B`) to generate a grounded answer. Retrieval quality is measured with recall@k.

## Description

A language model only knows what it was trained on. Instead of retraining it, RAG lets the model look up evidence in an external source at answer time. This project builds the full pipeline:

1. **Indexing**: read the corpus, split each file into chunks, and persist a searchable index.
2. **Retrieving**: given a question, return the top-k source locations (`file_path` + character range).
3. **Augmenting**: place the retrieved snippets in the model's prompt.
4. **Generating**: produce a short answer grounded in those snippets.
5. **Evaluating**: compute recall@k against a ground-truth dataset.

All commands are exposed through a Python Fire CLI, and the data exchanged between stages is validated with pydantic models.

## Instructions

### Requirements

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) (the project and package manager)
- Several GB of free disk space (PyTorch and the model weights)
- The vLLM repository placed under `data/raw/` (so that files live at `data/raw/vllm-0.10.1/...`) and the question datasets under `data/datasets/`

### Installation

```bash
make install     # runs `uv sync`
```

### Makefile rules

| Rule | Description |
|---|---|
| `make install` | Install dependencies with `uv sync` |
| `make index` | Build the index (once)
| `make run` | Run the main module (the full pipeline)|
| `make search` | Single-query search |
| `make search_dataset` | Search a whole dataset (scope the output directory by dataset) |
| `make evaluate` | Measure recall@k |
| `make answer` | Answer a single question |
| `make answer_dataset` | Generate answers for a whole dataset |
| `make debug` | Run the main module under `pdb` |
| `make lint` | `flake8` + `mypy` with the mandatory flags |
| `make lint-strict` | `flake8` + `mypy --strict` |
| `make clean` | Remove `__pycache__` and `.mypy_cache` |

### Expected layout

```
.
├── src/                     # implementation (run with `python -m src`)
├── data/
│   ├── raw/                 # the vLLM repository (indexed sources)
│   ├── processed/           # index produced by `index`
│   ├── datasets/
│   │   ├── UnansweredQuestions/
│   │   └── AnsweredQuestions/
│   └── output/
│       ├── search_results/<DatasetScope>/
│       └── search_results_and_answer/<DatasetScope>/
├── pyproject.toml
├── uv.lock
├── Makefile
└── README.md
```

`data/` is git-ignored: the evaluator generates the index and outputs itself.

### CLI commands

Every command is invoked as `uv run python -m src <command> [options]`.

| Command | Description |
|---|---|
| `index --max_chunk_size <int>` | Ingest `data/raw/` and build the index under `data/processed/` (default 2000, maximum 2000) |
| `search <query> --k <int>` | Print the top-k sources for one query as `path [first:last]` |
| `search_dataset --dataset_path <path> --k <int> --save_directory <dir>` | Run search over a dataset and write a `StudentSearchResults` JSON |
| `answer <query> --k <int>` | Retrieve context and generate an answer for one query |
| `answer_dataset --student_search_results_path <path> --save_directory <dir>` | Generate answers for a search results file and write a `StudentSearchResultsAndAnswer` JSON |
| `evaluate --student_search_results_path <path> --dataset_path <path>` | Print recall@1/3/5/10 against a ground-truth dataset (for own testing) |

## Example usage

```bash
# 1. Build the index (once) - make index
uv run python -m src index --max_chunk_size 2000

# 2. Single-query search - make search
uv run python -m src search "How to configure the OpenAI server?" --k 5

# 3. Search a whole dataset (scope the output directory by dataset) - make search_dataset
uv run python -m src search_dataset \
  --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
  --k 10 \
  --save_directory data/output/search_results/UnansweredQuestions

# 4. Measure recall@k - make evaluate
uv run python -m src evaluate \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json

# 5. Answer a single question - make answer
uv run python -m src answer "What HTTP endpoint is used to load a LoRA adapter?" --k 5

# 6. Generate answers for a whole dataset - make answer_dataset
uv run python -m src answer_dataset \
  --student_search_results_path data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
  --save_directory data/output/search_results_and_answer/UnansweredQuestions
```
Example output of `evaluate`:

```
Total number of questions evaluated: 100
Missing questions: 0
Recall@1: 0.620 (62.0%)
Recall@3: 0.780 (78.0%)
Recall@5: 0.820 (82.0%)
Recall@10: 0.900 (90.0%)
```

## System architecture

```
Corpus (data/raw)
   -> Chunked        (discovery, reading, chunking)        src/chunker.py
   -> Indexer        (BM25 index + chunk store, save/load) src/indexer.py
   -> search         (query -> top-k chunks)               src/indexer.py
   -> Generator      (prompt + Qwen3-0.6B)                 src/generator.py
   -> JSON output    (pydantic models)                     src/models.py
Evaluate (recall@k with IoU > 0.05)                        src/cli.py
```

| Module | Role |
|---|---|
| `__main__.py` | Entry point: runs Fire on `CLIConfig` and acts as a last-resort error handler |
| `cli.py` | `CLIConfig`: one thin method per command, plus the IoU / recall functions used by `evaluate` |
| `chunker.py` | `Chunked`: finds files, reads them, splits them into `Chunk` objects |
| `indexer.py` | `Indexer`: builds, saves, loads and queries the BM25 index |
| `generator.py` | `Generator`: loads the model, builds the chat prompt, generates the answer |
| `models.py` | Pydantic models (the subject's models plus an internal `Chunk`) |
| `errors.py` | Custom exception hierarchy rooted at `RagError` |

Each CLI command is an isolated entry point that loads what it needs. The commands share the underlying modules, not state. `Chunk` extends `MinimalSource` with a `text` field and is only used internally: it is never written to the output files, which contain `MinimalSource` objects only.

### Persisted index

`index` writes to `data/processed/`:

- the BM25 files produced by `bm25s` (sparse matrix arrays, `vocab.index.json`, `params.index.json`)
- `chunks.json`: every chunk (path, offsets, text) in exactly the order it was indexed, because the position returned by BM25 is the only link between a score and a chunk

At load time the BM25 document count is compared with the number of chunks, so a half-written index is detected instead of silently mapping positions to the wrong chunks.

## Chunking strategy

- **Files indexed**: `.py`, `.md` and `.txt` files under `data/raw/`. Other formats are skipped, which keeps indexing fast.
- **Two strategies** (LangChain `RecursiveCharacterTextSplitter.from_language`):
  - **Python** (`Language.PYTHON`): prefers to cut at `class` / `def` boundaries, then falls back to blank lines, lines and spaces.
  - **Markdown / text** (`Language.MARKDOWN`): prefers headers, then code fences, paragraphs and lines. `.txt` files use this strategy as a generic fallback.
- **Chunk size**: configurable with `--max_chunk_size`, default 2000 characters, capped at 2000 because the grader rejects any longer source.
- **Overlap**: 20% of the chunk size, derived from `--max_chunk_size` so one value controls both.
- **Offsets**: obtained with `add_start_index=True`; the end index is `start + len(chunk)` (exclusive, like a Python slice). Files are always read with `utf-8` and `newline=""`, so `\r\n` is never translated and offsets stay valid against the raw file.
- **Whitespace**: the splitter strips whitespace at chunk boundaries, so consecutive chunks can have small gaps that contain only whitespace.
- **Verification**: for the whole corpus, `text[first:last]` was checked to equal the stored chunk, and no gap between consecutive chunks of a file contained non-whitespace characters.

## Retrieval method

- **Algorithm**: BM25 through the `bm25s` library (default parameters and scoring variant).
- **Tokenization**: the default `bm25s` tokenizer, applied identically to chunks at index time and to queries at search time (one shared function, `tokenize_texts`).
- **Search**: the query is tokenized and scored against the sparse index. The top-k positions are mapped back to `Chunk` objects. `k` is clamped to the number of chunks, and results with a score of 0 are dropped, so a query with no known words returns no results instead of arbitrary chunks.
- **Loading**: the index is loaded with `mmap=True` to keep cold starts short, and loaded once per command (never per question in dataset commands).

## Answer generation

- **Model**: `Qwen/Qwen3-0.6B`, loaded once per command with `transformers`.
- **Prompt**: a chat-format prompt (rendered with the tokenizer's chat template). The system message tells the model to answer only from the provided context, to say so when the context lacks the answer, and to be concise. The user message holds the numbered snippets (each labelled with its file path) followed by the question, placed last.
- **Decoding**: greedy (`do_sample=False`), thinking mode disabled, at most 256 new tokens. Only the newly generated tokens are decoded, and any `<think>` block is stripped.
- **Dataset mode**: `answer_dataset` reuses the retrieval stored in the search results file instead of searching again. Since that file contains no text, snippets are rebuilt by re-reading each source file and slicing `[first:last]`. File contents are cached across questions.
- **No context**: if no snippet is available, the model is not called and a fixed "no relevant information" answer is returned.

## Performance analysis

Results on the public datasets (BM25, default tokenizer, `--max_chunk_size 2000`, `--k 10`), computed with the project's own `evaluate` command:

| Dataset | Questions | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Target (@5) |
|---|---|---|---|---|---|---|
| Docs | 100 | 62.0% | 78.0% | 82.0% | 90.0% | 80% |
| Code | 99 | 32.3% | 47.5% | 58.6% | 63.6% | 50% |

Both datasets reach their recall@5 threshold. The code side is weaker, as expected: questions paraphrase behaviour in natural language while the code uses identifiers (for example `max_num_batched_tokens`), and the default tokenizer keeps such identifiers as a single token, so the words rarely meet. Recall grows steadily with k, which means the right chunk is often retrieved but ranked low.

System performance (fill in with your own measurements):

| Metric | Measured | Limit |
|---|---|---|
| Indexing time (whole corpus) | TODO | 5 min |
| Chunks indexed | TODO | n/a |
| Search over 200 questions | TODO | 90 s |
| Answer generation, per question (CPU) | TODO | n/a |

Effect of the chunk size on recall@5 (fill in if you ran the comparison):

| `--max_chunk_size` | Docs recall@5 | Code recall@5 |
|---|---|---|
| 500 | TODO | TODO |
| 1000 | TODO | TODO |
| 2000 | 82.0% | 58.6% |

## Design decisions

- **BM25 over TF-IDF**: it handles chunk length and repeated terms better, and `bm25s` is fast enough for the throughput limit.
- **LangChain splitters**: language-aware separators give two distinct strategies with little code, and a single pass over the full text keeps offsets reliable.
- **Chunks stored with their text**: roughly 25 MB at this scale, and it avoids re-reading files at query time. The text is stripped from every output file.
- **`Chunk` subclassing `MinimalSource`**: the output model stays exactly as in the subject, and the extra field lives only in an internal model.
- **Explicit persistence of chunks**: `chunks.json` is written next to the BM25 files, in index order, rather than relying on the library's corpus storage.
- **Pure, small functions**: chunk splitting, tokenizing, IoU and per-question recall take plain inputs and return plain outputs, so each can be tested alone.
- **Own `evaluate`**: recall@k follows the subject's rule (same `file_path` and IoU > 0.05), is computed per question and averaged over the ground-truth questions, and counts questions missing from the results as 0.
- **Dataset commands reuse saved retrieval**: `answer_dataset` consumes the output of `search_dataset`, so the sources in the answers are exactly the ones that were scored.
- **Error handling**: expected failures raise exceptions deriving from `RagError`; `__main__` prints them instead of showing a traceback.

## Challenges faced

- **Offsets and whitespace**: gaps between consecutive chunks looked suspicious at first. A check comparing every gap against the original file showed they only contain whitespace stripped by the splitter.
- **Reading files without altering offsets**: forcing `utf-8` and `newline=""` guarantees the same characters at chunking time and at answer time.
- **Identifiers vs. natural language**: code questions score lower because the question's words and the code's identifiers differ. Splitting `snake_case` / `camelCase` while keeping the full identifier is the main improvement to explore.
- **Chaining splitters**: a header splitter followed by a size splitter produces offsets relative to each section, not the file, so a single-pass recursive splitter was chosen.
- **Model typing**: `transformers` and `mypy` disagree on `generate`, solved by annotating the model as `Any`.
- **Dataset layout**: the search results file and the question dataset have different top-level keys (`search_results` vs. `rag_questions`), so each command validates its input with the matching pydantic model.

## Resources

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020)](https://arxiv.org/abs/2005.11401)
- [Okapi BM25 (Wikipedia)](https://en.wikipedia.org/wiki/Okapi_BM25)
- [bm25s documentation](https://github.com/xhluca/bm25s)
- [LangChain text splitters](https://python.langchain.com/docs/concepts/text_splitters/)
- [Hugging Face Transformers: chat templates](https://huggingface.co/docs/transformers/chat_templating)
- [Qwen3-0.6B model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Python Fire](https://github.com/google/python-fire) and [pydantic](https://docs.pydantic.dev/)
- [uv documentation](https://docs.astral.sh/uv/)

### How AI was used

An AI assistant (Claude) was used as a tutor and reviewer, not as a code generator to paste from:

- **Design discussions**: how to model chunks, where to separate chunking, indexing and the CLI, what to persist, and how recall@k and the IoU matching work.
- **Library guidance**: which LangChain, `bm25s` and `transformers` classes and parameters exist and what they do (chat templates, tokenization, generation, memory mapping).
- **Code review and debugging**: finding bugs in my own code (file reading, shared list state, positional matching in the evaluation, wrong key names, output wrapping, `mkdir` before writing) and explaining why each fix was needed.
- **Evaluation logic**: reasoning about the metric before writing `evaluate`, and checking that my output format matched the subject.
- **Documentation**: drafting this README from the code and the subject.

Every suggestion was tested and checked, for example by verifying chunk offsets over the whole corpus and comparing results, and I can explain every part of the code.

## Limitations and possible improvements

- Tokenization: split `snake_case` / `camelCase` identifiers while keeping the full identifier; try stemming and stopword removal; tune BM25's `k1` and `b`.
- Chunk size and overlap: compare smaller sizes, especially for code.
- Bonus ideas: semantic embeddings with a lightweight CPU model, hybrid retrieval, incremental indexing, caching, a local HTTP API.