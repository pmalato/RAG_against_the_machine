from pathlib import Path
from json import load, dump
from .chunker import Chunked
from .indexer import Indexer
from .models import (
    Chunk,
    MinimalSource,
    MinimalSearchResults
    )
from .errors import (
    InvalidChunkSizeError,
    MissingDirectoryError,
    )

CODE: str = "dataset_code_public.json"
DOCS: str = "dataset_docs_public.json"


class CLIConfig():
    def __init__(self) -> None:
        ...

    def index(self, max_chunk_size: int = 2000) -> None:
        """Takes all files in 'data/raw' accepting only '.md', '.txt'
        and '.py' formats. Using the LangChain module, separates every
        valid file into chunks with size up to inputed 'max_chunk_size'.
        These chunks are validated with the help of the pydantic module.
        Finally, uses bm25s module to store every chunk into 'data/processed/'.
        Adittional informative files are added in 'data/processed' folder
        as well.
        """
        if max_chunk_size <= 0 or max_chunk_size > 2000:
            raise InvalidChunkSizeError
        builder: Chunked = Chunked()
        builder.chunk_files(max_chunk_size)
        chunks: list[Chunk] = builder.get_processed()
        indexer: Indexer = Indexer()
        indexer.build_chunks(chunks)
        indexer.save_processed()

    def search(self, query: str, k: int = 10) -> list[Chunk]:
        indexer: Indexer = Indexer.load_processed()
        return indexer.search(query, k)

    def search_dataset(
            self, dataset_path: str,
            save_directory: str = "data/output/"
            "search_results/UnansweredQuestions", k: int = 10) -> None:
        if not save_directory.startswith("data/output/"):
            raise MissingDirectoryError(
                "Your answers must go to 'data/output/'")
        if not dataset_path:
            raise MissingDirectoryError("Invalid path for 'dataset_path'")
        if not save_directory:
            raise MissingDirectoryError("Invalid path for 'save_directory'")
        end: str = DOCS if dataset_path.endswith(DOCS) else CODE
        source: Path = Path(dataset_path)
        target: Path = Path(save_directory)
        res: list[MinimalSearchResults] = []
        try:
            with open(source, encoding="utf-8") as file:
                data: dict[str, list[dict[str, str]]] = load(file)
            for d in data["rag_questions"]:
                id: str = d["question_id"]
                query: str = d["question"]
                chunks: list[MinimalSource] = [MinimalSource(
                    **chk.model_dump(exclude={"text"}))
                    for chk in self.search(query, k)]
                res += [MinimalSearchResults(
                    question_id=id, question=query, retrieved_sources=chunks)]
            target.mkdir(parents=True, exist_ok=True)
            with open(target / end, "w", encoding="utf-8") as resolve:
                dump([piece.model_dump() for piece in res], resolve)
            print(f"Saved student_search_results to '{save_directory}'")
        except OSError as e:
            print(e)

    def answer(self, query: str, k: int = 10) -> None:
        ...

    def answer_dataset(
            self, student_search_results_path: str,
            save_directory: str, k: int = 10) -> None:
        ...

    def evaluate(
            self, student_search_results_path: str,
            dataset_path: str) -> None:
        ...
