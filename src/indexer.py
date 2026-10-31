from bm25s import BM25, tokenize
from pathlib import Path
from json import dump, load
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
    def load_processed(cls, directory: str = "data/processed/") -> "Indexer":
        """Restore an Indexer from a directory written by save_processed."""
        source: Path = Path(directory)
        if not directory or not source.is_dir():
            raise MissingDirectoryError
        try:
            retriever: BM25 = BM25.load(directory, mmap=True)
            with open(source / CHUNKS_FILE, encoding="utf-8") as res:
                raw = load(res)
                chunks: list[Chunk] = [
                    Chunk.model_validate(item) for item in raw]
        except (OSError, ValueError, TypeError):
            raise MissingIndexError
        if retriever.scores["num_docs"] != len(chunks):
            raise MissingIndexError
        indexer: Indexer = cls()
        indexer._retriever = retriever
        indexer._chunks = chunks
        return indexer

    def search(self, query: str, k: int) -> list[Chunk]:
        """Return the top-k chunks for a query, best first."""
        if k <= 0 or not query.strip():
            return []
        return []

    def get_chunks(self) -> list[Chunk]:
        return self._chunks
