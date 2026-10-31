from bm25s import BM25, tokenize
from pathlib import Path
from json import dump
# from pydantic import ValidationError
from .models import Chunk
from .errors import (
    AccessFilesError,
    MissingattributesError,
    MissingDirectoryError,
    MissingIndexError
)

CHUNKS_FILE: str = "chunks.json"


def tokenize_texts(
        texts: list[str], show_progress: bool = True) -> list[list[str]]:
    """Turns texts into token lists (same function for docs and queries)."""
    tokens: list[list[str]] = tokenize(
        texts, show_progress=show_progress, return_ids=False)
    return tokens


class Indexer():
    """BM25 index over chunks, with save/load support."""
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._retriever: BM25 = BM25()

    def build_chunks(self, chunks: list[Chunk]) -> None:
        """Tokenize the chunk texts and build the BM25 index."""
        if not chunks:
            raise MissingattributesError
        tokens: list[list[str]] = tokenize_texts(
            [chunk.text for chunk in chunks])
        retriever = BM25()
        retriever.index(tokens)
        self._chunks = chunks
        self._retriever = retriever

    def save_processed(self, directory: str = "data/processed/") -> None:
        """Write the BM25 files and chunks.json into the directory."""
        if self._retriever is None or not self._chunks:
            raise MissingattributesError
        if not directory:
            raise MissingDirectoryError
        target = Path(directory)
        try:
            target.mkdir(parents=True, exist_ok=True)
            self._retriever.save(str(target))
            with open(target / CHUNKS_FILE, 'w', encoding="utf-8") as resolve:
                dump([chk.model_dump() for chk in self._chunks], resolve)
        except OSError:
            raise AccessFilesError

    @classmethod
    def load_processed(cls, directory: str = "data/processed/") -> Indexer:
        if not directory:
            raise MissingDirectoryError
        object = cls()
        chunks = object.get_chunks()
        retriever = object.get_retriever()
        if not chunks or not retriever:
            raise MissingattributesError
        try:
            retriever.load(directory, mmap=True)
        except FileNotFoundError:
            raise MissingIndexError
        tokens: list[list[str]] = tokenize(retriever)
        retriever.index(tokens)
        return object

    def search(self, query: str, k: int) -> list[Chunk]:
        if k <= 0 or query == "":
            return []
        return []

    def get_chunks(self) -> list[Chunk]:
        return self._chunks

    def get_retriever(self) -> BM25:
        return self._retriever
