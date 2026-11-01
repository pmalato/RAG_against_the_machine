from pathlib import Path
from json import load, dump
from .chunker import Chunked
from .models import Chunk
from .indexer import Indexer
from .errors import (
    InvalidChunkSizeError,
    MissingDirectoryError)


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

    def search(self, query: str, k: int = 10) -> None:
        indexer: Indexer = Indexer.load_processed()
        chunks: list[Chunk] = indexer.search(query, k)
        [print(
            x.file_path, x.first_character_index,
            x.last_character_index) for x in chunks]

    def search_dataset(
            self, dataset_path: str = "data/datasets/UnansweredQuestions/"
            "dataset_docs_public.json",
            save_directory: str = "data/output/search_results/"
            "UnansweredQuestions", k: int = 10) -> None:
        if not dataset_path:
            raise MissingDirectoryError("Invalid path for 'dataset_path'")
        if not save_directory:
            raise MissingDirectoryError("Invalid path for 'save_directory'")
        source: Path = Path(dataset_path)
        target: Path = Path(save_directory)
        for f in source.glob('*'):
            with open(f, encoding="utf-8") as file:
                data: dict[str, list[dict[str, str]]] = load(file)
            indexer: Indexer = Indexer.load_processed()
            

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
